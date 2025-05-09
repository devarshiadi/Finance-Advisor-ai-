from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.database import get_db
from app.auth import get_current_active_user
from app.main import templates # Import templates from main.py
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/home", response_class=HTMLResponse)
async def user_homepage(request: Request): # Removed: current_user: models.User = Depends(get_current_active_user)
    # User data will be fetched and displayed by client-side JavaScript
    return templates.TemplateResponse("user/homepage.html", {
        "request": request,
        # "user": current_user, # This will be handled by client-side JS
        "title": "User Homepage"
    })

@router.get("/chatbot/{model_type}", response_class=HTMLResponse)
async def chatbot_page(request: Request, model_type: str): # Removed: current_user: models.User = Depends(get_current_active_user)
    # Client-side JS on chatbot.html already handles token for API submission.
    # This route now just serves the page structure.
    valid_models = ["base", "enhanced", "rule_based"]
    if model_type.lower() not in valid_models:
        raise HTTPException(status_code=404, detail="Model type not found")

    # Prepare context for the template based on model_type
    # This context will help the template render the correct form fields
    form_fields = []
    page_title = ""

    if model_type == "base":
        page_title = "Base Model Advisor"
        form_fields = [
            {"name": "Salary", "label": "Monthly Salary (₹)", "type": "number", "required": True, "min": 0},
            {"name": "Expenses", "label": "Monthly Expenses (₹)", "type": "number", "required": True, "min": 0},
            {"name": "Savings", "label": "Monthly Savings (₹)", "type": "number", "required": True, "min": 0},
            {"name": "Lifecycle_Stage", "label": "Lifecycle Stage", "type": "select", "required": True, "options": ["Student", "Early Career", "Mid-Career", "Late Career", "Retired"]},
            {"name": "Risk_Appetite", "label": "Risk Appetite", "type": "select", "required": True, "options": ["Low", "Medium", "High"]},
            {"name": "Investment_Horizon", "label": "Investment Horizon", "type": "select", "required": True, "options": ["Short-term", "Medium-term", "Long-term"]},
        ]
    elif model_type == "enhanced":
        page_title = "Enhanced Model Advisor"
        
        # Define the options for dropdowns based on provided lists
        cities = sorted([
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Jaipur',
            'Kochi', 'Kolkata', 'Ahmedabad', 'Gurgaon', 'Lucknow', 'Nagpur', 'Chandigarh',
            'Surat', 'Indore', 'Bhopal'
        ])
        
        professions = sorted([
            'Software Engineer', 'Doctor', 'Retired Banker', 'Student', 'Marketing Manager', 'Teacher', 
            'Freelancer', 'Architect', 'Business Owner', 'Nurse', 'Product Manager', 'CA', 'Data Analyst', 
            'Retired Professor', 'Journalist', 'Graphic Designer', 'Sales Executive', 'HR Manager', 'Intern',
            'Dentist', 'Lawyer', 'Content Creator', 'Pensioner', 'UX Designer', 'Government Employee', 
            'Fashion Designer', 'Startup Founder', 'Homemaker (Investor)', 'Investment Banker', 'IT Consultant',
            'College Student', 'Pharmacist', 'Textile Business Owner', 'Event Planner', 'Film Producer', 
            'Nutritionist', 'Retired Army Officer', 'Social Media Manager', 'Airline Pilot', 'Biotech Researcher',
            'Real Estate Agent', 'AI Engineer', 'Retired Teacher', 'Financial Analyst', 'Software Developer', 
            'NGO Director', 'Fitness Trainer', 'Digital Marketer', 'Content Strategist', 'Retired Engineer', 
            'UI Developer', 'Operations Manager', 'Corporate Lawyer', 'School Principal', 'AI Researcher', 
            'Junior Doctor', 'Finance Manager', 'Fashion Blogger', 'HR Consultant', 'Video Editor', 
            'Small Business Owner', 'Dietitian', 'Supply Chain Manager', 'Interior Designer', 'Sales Manager', 
            'PR Executive', 'Logistics Head', 'Content Writer', 'Retired Govt. Employee', 'Marketing Lead', 
            'IT Manager', 'Startup Intern', 'Export Manager', 'Fitness Instructor', 'Real Estate Broker', 
            'Event Manager', 'Software Trainee', 'Data Scientist', 'HR Director', 'Hotel Manager', 
            'Social Worker', 'Cybersecurity Expert', 'E-commerce Manager', 'Bank Manager', 'Retired IT Manager', 
            'UX Researcher', 'Product Designer', 'Cybersecurity Analyst', 'Podcast Producer', 'E-commerce Seller',
            'Cloud Architect', 'Corporate Trainer', 'AI Trainer', 'Supply Chain Head', 'Product Owner', 
            'UI/UX Designer', 'Finance Director', 'Sustainability Consultant', 'Retired Bank Manager', 
            'Social Media Influencer', 'Blockchain Developer', 'NGO Head', 'Data Engineer', 'Event Curator', 
            'CTO', 'Content Marketer', 'Retired Army Major', 'AR/VR Developer', 'Logistics Manager', 'VP Sales',
            'EdTech Founder', 'SEO Specialist', 'Yoga Instructor', 'IT Director', 'App Developer', 
            'Consultant Cardiologist', 'Freelance Writer', 'Cloud Engineer', 'Retired CA', 'Digital Artist', 
            'Retired Pilot', 'Graphic Animator', 'AI Ethicist', 'School Trustee', 'Robotics Engineer', 
            'Fashion Stylist', 'Retired Nurse', 'AI Ethics Consultant', 'Drone Engineer', 'Retired Bank Clerk', 
            'Digital Nomad', 'CFO', 'Sustainability Analyst', 'Retired Journalist', 'Social Entrepreneur', 
            'DevOps Engineer', 'School Counselor', 'Retired Army Colonel', 'AR Developer', 'Sales Director', 
            'EdTech Consultant', 'SEO Expert', 'Cardiologist', '3D Artist', 'HR Head', 'Animator', 
            'Fashion Influencer'
        ])

        form_fields = [
            {"name": "Profession", "label": "Profession", "type": "select", "required": True, "options": professions},
            {"name": "City", "label": "City", "type": "select", "required": True, "options": cities},
            {"name": "Salary", "label": "Monthly Salary (₹)", "type": "number", "required": True, "min": 0},
            {"name": "Expenses", "label": "Monthly Expenses (₹)", "type": "number", "required": True, "min": 0},
            {"name": "Savings", "label": "Monthly Savings (₹)", "type": "number", "required": True, "min": 0},
            {"name": "Lifecycle_Stage", "label": "Lifecycle Stage", "type": "select", "required": True, "options": ["Student", "Early Career", "Mid-Career", "Late Career", "Retired"]},
            {"name": "Risk_Appetite", "label": "Risk Appetite", "type": "select", "required": True, "options": ["Low", "Medium", "High"]},
            {"name": "Investment_Horizon", "label": "Investment Horizon", "type": "select", "required": True, "options": ["Short-term", "Medium-term", "Long-term"]},
        ]
    elif model_type == "rule_based":
        page_title = "Rule-Based Advisor"
        form_fields = [
            {"name": "Lifecycle_Stage", "label": "Lifecycle Stage", "type": "select", "required": True, "options": ["Student", "Early Career", "Mid-Career", "Late Career", "Retired"]},
            {"name": "Risk_Appetite", "label": "Risk Appetite", "type": "select", "required": True, "options": ["Low", "Medium", "High"]},
            {"name": "Investment_Horizon", "label": "Investment Horizon", "type": "select", "required": True, "options": ["Short-term", "Medium-term", "Long-term"]},
            {"name": "Annual_Salary_Package", "label": "Annual Salary Package (CTC) (₹)", "type": "number", "required": True, "min": 0},
            {"name": "Monthly_In_hand_Salary", "label": "Actual Monthly In-hand Salary (₹)", "type": "number", "required": True, "min": 0},
            {"name": "Total_Monthly_Expenses", "label": "Total Estimated Monthly Expenses (₹)", "type": "number", "required": True, "min": 0},
        ]
        
    return templates.TemplateResponse("user/chatbot.html", {
        "request": request,
        # "user": current_user, # Client-side JS on this page handles API calls with token
        "title": page_title,
        "model_type": model_type,
        "form_fields": form_fields
    })

@router.get("/recommendations", response_class=HTMLResponse)
async def recommendations_page(request: Request): # Removed: current_user: models.User = Depends(get_current_active_user)
    # Client-side JS could be added to this page if it needs to display user-specific info
    # or make authenticated API calls for dynamic market data.
    # For now, it serves static structure with mocked data.
    # Data fetching logic would go into services/market_data_service.py
    # For now, just rendering a template.
    market_data = { # Mock data
        "stocks": [
            {"name": "Reliance Industries", "price": "2,850.50 INR", "change": "+0.5%"},
            {"name": "Tata Consultancy Services", "price": "3,900.75 INR", "change": "-0.2%"},
            {"name": "HDFC Bank", "price": "1,500.20 INR", "change": "+1.1%"},
        ],
        "gold_price": "96,172.27 -745.25 INR per 10g",
        "recommended_stocks": [
            {"name": "Infosys", "reason": "Strong growth potential in IT sector."},
            {"name": "ICICI Bank", "reason": "Good financial performance and outlook."}
        ]
    }
    return templates.TemplateResponse("user/recommendations.html", {
        "request": request,
        # "user": current_user, # Can be fetched by client-side JS if needed
        "title": "Market Trends & Recommendations",
        "market_data": market_data
    })
