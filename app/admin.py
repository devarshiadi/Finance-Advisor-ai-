from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, crud
from app.database import get_db
from app.auth import get_current_admin_user, get_current_active_user # Import both
from app.main import templates # Import templates from main.py

router = APIRouter()

# Route to serve the HTML shell for the dashboard
@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard_shell(request: Request):
    # This route loads the page structure.
    # Client-side JS will verify admin status and fetch data.
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "title": "Admin Dashboard"
        # No user or users_list passed here initially
    })

# New API endpoint to fetch dashboard data (protected)
@router.get("/api/dashboard-data")
async def get_admin_dashboard_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user), # Ensures only admin can access
    search_query: str = Query(None, alias="search")
):
    if search_query:
        user = crud.get_user_by_email(db, email=search_query)
        users_list = [schemas.User.from_orm(user)] if user else [] # Convert to schema
    else:
        users = crud.get_users(db, limit=100)
        users_list = [schemas.User.from_orm(u) for u in users] # Convert list to schema

    # Return data needed by the dashboard template's JS
    return {"users_list": users_list, "search_query": search_query, "admin_email": current_user.email}


# Route to view specific user details (protected)
# This serves an HTML page, so it will also need the client-side auth check pattern
@router.get("/users/{user_id}", response_class=HTMLResponse)
async def admin_view_user_details_shell(request: Request, user_id: int):
    # Serve the shell page. JS will fetch details.
     return templates.TemplateResponse("admin/user_details.html", {
        "request": request,
        "user_id": user_id, # Pass user_id for JS to use
        "title": f"User Details" # Generic title initially
    })

# New API endpoint to fetch specific user details (protected)
@router.get("/api/users/{user_id}")
async def get_admin_user_details_data(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user) # Ensure admin access
):
    target_user = crud.get_user(db, user_id=user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_inputs_orm = crud.get_user_data_inputs_by_user_id(db, user_id=user_id, limit=100)
    
    # Convert ORM objects to Pydantic schemas for JSON response
    target_user_schema = schemas.User.from_orm(target_user)
    user_inputs_schema = [schemas.UserDataInputResponse.from_orm(item) for item in user_inputs_orm]

    return {
        "target_user": target_user_schema,
        "user_inputs": user_inputs_schema
    }
