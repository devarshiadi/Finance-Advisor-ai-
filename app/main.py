from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from sqlalchemy.orm import Session

from app import models, schemas, crud, auth # app. is used if main.py is outside app/
from app.database import engine, get_db, create_db_and_tables
from app.services import chatbot_service, data_service # app.services
from app.auth import get_current_active_user, get_current_admin_user, oauth2_scheme # app.auth

# Determine the base directory of the 'app' package
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Financial Advisor Chatbot")

# Mount static files (CSS, JS, images)
# The path "static" here is relative to where main.py is.
# If main.py is in app/, then app/static/
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Setup Jinja2 templates
# If main.py is in app/, then app/templates/
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# --- Event Handlers ---
@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    # Initialize CSV file with headers if it doesn't exist
    data_service.initialize_csv()
    # Load ML models
    chatbot_service.load_models()
    # Create a default admin user if one doesn't exist (optional)
    db = next(get_db()) # Get a DB session
    try:
        admin_email = "admin@example.com"
        admin_password = "adminpassword" # Change this!
        
        admin_user_obj = crud.get_user_by_email(db, email=admin_email)
        
        if not admin_user_obj:
            print(f"Admin user '{admin_email}' not found, creating...")
            admin_user_schema = schemas.UserCreate(email=admin_email, password=admin_password, confirm_password=admin_password)
            crud.create_admin_user(db, admin_user_schema)
            print(f"Default admin user '{admin_email}' created with password '{admin_password}'. PLEASE CHANGE THE PASSWORD.")
        elif not admin_user_obj.is_admin:
            # If user exists but is not admin, update them (or log warning)
            print(f"User '{admin_email}' exists but is not admin. Updating status...")
            admin_user_obj.is_admin = True
            # If you also want to ensure the password is set, you might reset it here:
            # admin_user_obj.hashed_password = security.get_password_hash(admin_password)
            db.add(admin_user_obj) # Add the existing object to the session to track changes
            db.commit()
            print(f"User '{admin_email}' updated to be an admin.")
        else:
             print(f"Admin user '{admin_email}' already exists.")

    except Exception as e:
        print(f"Error during admin user setup: {e}")
    finally:
        db.close()


# --- Include Routers ---
# Assuming auth.py, user.py, admin.py are in the same directory as main.py (i.e. in 'app')
# If main.py is in the root, these would be from app.auth, app.user, app.admin
from . import auth as auth_router # Renaming to avoid conflict with 'auth' module
# We will create user_router and admin_router later
from . import user as user_router
from . import admin as admin_router

app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router.router, prefix="/user", tags=["User Pages"]) # User specific pages like /user/home
app.include_router(admin_router.router, prefix="/admin", tags=["Admin Pages"]) # Admin specific pages like /admin/dashboard

# --- Root and Basic Page Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Redirect to login page by default, or to home if logged in (more complex logic for latter)
    return templates.TemplateResponse("auth/login.html", {"request": request, "title": "Login"})

@app.get("/signup-page", response_class=HTMLResponse) # Renamed to avoid conflict if auth router has /signup
async def signup_page_render(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request, "title": "Sign Up"})

@app.get("/login-page", response_class=HTMLResponse) # Renamed to avoid conflict if auth router has /login
async def login_page_render(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request, "title": "Login"})

# The actual /home and /admin/dashboard routes are now in user.py and admin.py respectively.

# --- Chatbot API endpoint ---
@app.post("/api/chatbot", response_model=schemas.ChatbotInteractionResponse)
async def api_chatbot_interact(
    request_data: schemas.ChatbotInteractionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Process the interaction using the chatbot service
    response = chatbot_service.process_chatbot_interaction(request_data)

    # If no error in recommendation, save input and potentially output to DB and CSV
    if "error" not in response.recommendation:
        # Save to DB
        user_input_db = schemas.UserDataInputCreate(
            model_type=request_data.model_type,
            input_data=request_data.inputs
            # output_data=response.recommendation # Optionally store output
        )
        crud.create_user_data_input(db=db, item=user_input_db, user_id=current_user.id)

        # Save to CSV
        data_service.append_data_to_csv(
            user_id=current_user.id,
            user_email=current_user.email,
            model_type=request_data.model_type,
            input_data=request_data.inputs,
            output_data=response.recommendation # Pass the allocation part
        )
    
    return response

# --- Logout ---
@app.get("/logout")
async def logout(request: Request):
    # For token-based auth, logout is primarily a client-side operation (deleting the token).
    # Server-side, you might blacklist the token if using a more complex setup.
    # Here, we'll just redirect to the root path which serves the login page.
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND) # Changed url to "/"
    # Instruct browser to clear any relevant cookies if they were set by server (not typical for Bearer tokens)
    # response.delete_cookie("access_token_cookie") # If you were setting it as a cookie
    return response


# To run the app (example, usually done with uvicorn command line):
# if __name__ == "__main__":
#     import uvicorn
#     # Note: Uvicorn should typically be run from the project root, not from within app/
#     # e.g., uvicorn app.main:app --reload
#     # For direct execution from app/main.py (less common for FastAPI projects):
#     # uvicorn.run(app, host="0.0.0.0", port=8000)
#     # Better to run with: uvicorn financial_advisor.app.main:app --reload from the project root
#     # Or if main.py is in the root: uvicorn main:app --reload
#     pass
