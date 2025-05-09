import joblib
import pandas as pd
import os
from typing import Dict, Any, Tuple, List, Optional
from app import schemas # Assuming schemas.py is in the same 'app' directory
import logging

logger = logging.getLogger(__name__)

# --- Model Loading ---
# Define paths to the model files, assuming they are in app/ml_models/
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "ml_models") # app/ml_models
BASE_MODEL_PATH = os.path.join(MODEL_DIR, "basic_portfolio_model.pkl")
ENHANCED_MODEL_PATH = os.path.join(MODEL_DIR, "enhanced_portfolio_model.pkl")

# Ensure the ml_models directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Placeholder for loaded models
base_model_pipeline = None
enhanced_model_pipeline = None

def load_models():
    global base_model_pipeline, enhanced_model_pipeline
    try:
        if os.path.exists(BASE_MODEL_PATH):
            base_model_pipeline = joblib.load(BASE_MODEL_PATH)
            logger.info("Base model loaded successfully.")
        else:
            logger.error(f"Base model file not found at {BASE_MODEL_PATH}")

        if os.path.exists(ENHANCED_MODEL_PATH):
            enhanced_model_pipeline = joblib.load(ENHANCED_MODEL_PATH)
            logger.info("Enhanced model loaded successfully.")
        else:
            logger.error(f"Enhanced model file not found at {ENHANCED_MODEL_PATH}")
    except Exception as e:
        logger.error(f"Error loading ML models: {e}")

# Call load_models when this module is imported so they are ready.
# load_models() # Will be called from main.py or an init step

# --- Base Model Prediction ---
def predict_base_model(input_data: schemas.BaseModeInputSchema) -> Dict[str, float]:
    if not base_model_pipeline:
        logger.error("Base model not loaded. Cannot predict.")
        # Consider raising an exception or returning an error state
        return {"error": "Base model not available"}

    try:
        data = input_data.dict()
        
        # Convert categorical features using mappings from the loaded pipeline
        # These mappings should exist in the .pkl file if saved correctly
        processed_data = data.copy()
        processed_data['Lifecycle_Stage'] = base_model_pipeline['mappings']['lifecycle'][data['Lifecycle_Stage']]
        processed_data['Risk_Appetite'] = base_model_pipeline['mappings']['risk'][data['Risk_Appetite']]
        processed_data['Investment_Horizon'] = base_model_pipeline['mappings']['horizon'][data['Investment_Horizon']]

        # Create feature array in correct order (must match training)
        # Order from Reference/basemodel.py: Salary, Expenses, Savings, Lifecycle Stage, Risk Appetite, Investment Horizon
        X = [
            processed_data['Salary'],
            processed_data['Expenses'],
            processed_data['Savings'],
            processed_data['Lifecycle_Stage'], # This is now numerical
            processed_data['Risk_Appetite'],   # This is now numerical
            processed_data['Investment_Horizon'] # This is now numerical
        ]

        X_scaled = base_model_pipeline['scaler'].transform([X])
        pred = base_model_pipeline['model'].predict(X_scaled)[0]

        total = pred.sum()
        if total == 0: # Avoid division by zero
            return {'Equity': 0, 'Debt': 0, 'Gold': 0, 'FD/Cash': 0, "error": "Prediction resulted in zero total"}

        final_allocation = {
            'Equity': round((pred[0]/total)*100, 1),
            'Debt': round((pred[1]/total)*100, 1),
            'Gold': round((pred[2]/total)*100, 1),
            'FD/Cash': round((pred[3]/total)*100, 1)
        }
        return final_allocation
    except KeyError as e:
        logger.error(f"KeyError during base model prediction: {e}. Check mappings in pipeline or input data keys.")
        return {"error": f"Missing data or incorrect mapping for {e}"}
    except Exception as e:
        logger.error(f"Error in base model prediction: {e}")
        return {"error": str(e)}


# --- Enhanced Model Prediction ---
def predict_enhanced_model(input_data: schemas.EnhancedModelInputSchema) -> Dict[str, float]:
    if not enhanced_model_pipeline:
        logger.error("Enhanced model not loaded. Cannot predict.")
        return {"error": "Enhanced model not available"}

    try:
        data = input_data.dict()
        processed_data = data.copy()

        # Convert categorical features
        processed_data['Profession'] = enhanced_model_pipeline['profession_encoder'].transform([data['Profession']])[0]
        processed_data['City'] = enhanced_model_pipeline['city_encoder'].transform([data['City']])[0]
        processed_data['Lifecycle_Stage'] = enhanced_model_pipeline['mappings']['lifecycle'][data['Lifecycle_Stage']]
        processed_data['Risk_Appetite'] = enhanced_model_pipeline['mappings']['risk'][data['Risk_Appetite']]
        processed_data['Investment_Horizon'] = enhanced_model_pipeline['mappings']['horizon'][data['Investment_Horizon']]
        
        # Order from Reference/enhancedmodel.py:
        # ['Profession', 'City', 'Salary', 'Expenses', 'Savings', 'Lifecycle Stage', 'Risk Appetite', 'Investment Horizon']
        X = [
            processed_data['Profession'],
            processed_data['City'],
            processed_data['Salary'],
            processed_data['Expenses'],
            processed_data['Savings'],
            processed_data['Lifecycle_Stage'],
            processed_data['Risk_Appetite'],
            processed_data['Investment_Horizon']
        ]

        X_scaled = enhanced_model_pipeline['scaler'].transform([X])
        pred = enhanced_model_pipeline['model'].predict(X_scaled)[0]

        total = pred.sum()
        if total == 0:
             return {'Equity': 0, 'Debt': 0, 'Gold': 0, 'FD/Cash': 0, "error": "Prediction resulted in zero total"}

        final_allocation = {
            'Equity': round((pred[0]/total)*100, 1),
            'Debt': round((pred[1]/total)*100, 1),
            'Gold': round((pred[2]/total)*100, 1),
            'FD/Cash': round((pred[3]/total)*100, 1)
        }
        return final_allocation
    except KeyError as e:
        logger.error(f"KeyError during enhanced model prediction: {e}. Check mappings/encoders in pipeline or input data keys.")
        return {"error": f"Missing data or incorrect mapping/encoding for {e}"}
    except Exception as e:
        logger.error(f"Error in enhanced model prediction: {e}")
        return {"error": str(e)}

# --- Rule-Based Model Logic ---
# (Adapted from Reference/rulebasedmodel.py)

def _allocate_savings_rule_based(
    monthly_savings: float, 
    risk_profile: str, 
    horizon: str, 
    lifecycle: str
) -> Tuple[Dict[str, float], List[str]]:
    allocations = {}
    justification_points = [
        f"This allocation considers your {risk_profile} risk profile, {horizon} horizon, and {lifecycle} stage."
    ]
    risk_profile = risk_profile.lower() # Ensure consistency
    horizon = horizon.lower()
    # Lifecycle stage is already in a good format from schema e.g. "Early Career"

    if risk_profile == "low":
        allocations = {
            "Fixed Deposits / Recurring Deposits": 0.35,
            "Debt Mutual Funds (Liquid/Short Duration)": 0.30,
            "Gold (SGBs/ETFs)": 0.10,
            "Equity MFs (Large Cap/Index Funds)": 0.15,
            "Cash / Savings Account": 0.10
        }
        justification_points.append("- Focus on capital preservation and stable returns.")
    elif risk_profile == "medium":
        allocations = {
            "Equity MFs (Diversified - Large & Mid Cap/Flexi Cap)": 0.45,
            "Debt Mutual Funds": 0.25,
            "Fixed Deposits / PPF": 0.10,
            "Gold (SGBs/ETFs)": 0.10,
            "Equity MFs (International)": 0.05, 
            "Cash / Savings Account": 0.05
        }
        justification_points.append("- Aims for a balance between growth and stability.")
    elif risk_profile == "high":
        allocations = {
            "Equity MFs (Aggressive Growth - Mid/Small Cap, Thematic)": 0.60,
            "Equity MFs (International)": 0.15,
            "Direct Stocks (If experienced)": 0.10, 
            "Debt Mutual Funds (Strategic)": 0.05,
            "Gold (SGBs/ETFs - Tactical)": 0.05,
            "Alternative Inv. (REITs/InvITs)": 0.05
        }
        justification_points.append("- Focuses on maximizing long-term growth potential.")

    # Normalize percentages (simplified for brevity, original script had more robust normalization)
    current_total_percentage = sum(allocations.values())
    if abs(current_total_percentage - 1.0) > 0.001 and current_total_percentage != 0:
        factor = 1.0 / current_total_percentage
        allocations = {k: round(v * factor, 3) for k, v in allocations.items()} 
        # Adjust last item to make sum exactly 1.0 if needed due to rounding
        sum_val = sum(allocations.values())
        if sum_val != 1.0 and allocations:
            key_to_adjust = list(allocations.keys())[-1]
            allocations[key_to_adjust] += (1.0 - sum_val)
            allocations[key_to_adjust] = round(allocations[key_to_adjust], 3)


    # Convert percentage values to actual amounts based on monthly_savings
    # The chatbot response schema expects percentages for recommendation, so we return percentages.
    # The display logic in the template can calculate amounts.
    
    # For the ChatbotInteractionResponse, recommendation should be percentages
    # Let's ensure the values are percentages (0 to 100)
    final_percentage_allocations = {k: round(v * 100, 1) for k,v in allocations.items()}

    return final_percentage_allocations, justification_points


def _get_general_financial_tips(lifecycle_stage: str, monthly_savings: float, monthly_in_hand_salary: float) -> List[str]:
    tips = []
    if monthly_in_hand_salary > 0: # Avoid division by zero if salary is 0
        if monthly_savings <= 0 :
            tips.append("- Your expenses currently meet or exceed your income. Focus on creating a budget.")
        else:
            savings_rate = (monthly_savings / monthly_in_hand_salary) * 100
            tips.append(f"- Your current savings rate is approximately {savings_rate:.1f}%. Aim for at least 20-30%.")
    else: # No salary info or zero salary
        if monthly_savings <= 0:
             tips.append("- Your expenses currently meet or exceed your income. Focus on creating a budget.")


    tips.extend([
        "- Build & Maintain an Emergency Fund: Aim for 3-6 months of essential living expenses.",
        "- Get Adequately Insured: Health and Term Life Insurance are crucial.",
        "- Invest Regularly & Be Disciplined (e.g. SIPs).",
        "- Review Periodically: Revisit your financial plan annually or on major life events.",
        "- Understand Your Investments: Know the risks and costs."
    ])
    if lifecycle_stage == "Student" or lifecycle_stage == "Early Career":
        tips.append("- Focus on upskilling and career growth.")
    if lifecycle_stage == "Late Career/Pre-Retirement" or lifecycle_stage == "Retired": # Assuming "Retired" is a lifecycle stage
        tips.append("- Plan for healthcare expenses in retirement.")
    return tips

def predict_rule_based_model(input_data: schemas.RuleBasedModelInputSchema) -> Tuple[Dict[str, float], List[str], List[str]]:
    data = input_data.dict()
    
    monthly_savings = data['Monthly_In_hand_Salary'] - data['Total_Monthly_Expenses']

    if monthly_savings <= 0:
        allocation = {"message": "Savings are zero or negative. Focus on budgeting first."}
        justification = ["Investment allocation is not applicable without positive savings."]
        tips = _get_general_financial_tips(data['Lifecycle_Stage'], monthly_savings, data['Monthly_In_hand_Salary'])
        tips.insert(0, "Priority: Increase savings or reduce expenses.")
        return allocation, justification, tips

    allocation, justification = _allocate_savings_rule_based(
        monthly_savings,
        data['Risk_Appetite'],
        data['Investment_Horizon'],
        data['Lifecycle_Stage']
    )
    tips = _get_general_financial_tips(data['Lifecycle_Stage'], monthly_savings, data['Monthly_In_hand_Salary'])
    
    return allocation, justification, tips


# --- Main Chatbot Interaction Logic ---
def process_chatbot_interaction(
    request: schemas.ChatbotInteractionRequest
) -> schemas.ChatbotInteractionResponse:
    
    model_type = request.model_type.lower()
    inputs = request.inputs

    recommendation: Dict[str, Any] = {}
    justification: Optional[List[str]] = None
    tips: Optional[List[str]] = None

    try:
        if model_type == "base":
            # Validate inputs against BaseModeInputSchema
            validated_inputs = schemas.BaseModeInputSchema(**inputs)
            recommendation = predict_base_model(validated_inputs)
        elif model_type == "enhanced":
            validated_inputs = schemas.EnhancedModelInputSchema(**inputs)
            recommendation = predict_enhanced_model(validated_inputs)
        elif model_type == "rule_based":
            validated_inputs = schemas.RuleBasedModelInputSchema(**inputs)
            recommendation, justification, tips = predict_rule_based_model(validated_inputs)
        else:
            raise ValueError("Invalid model type specified")

        # Check for errors from prediction functions
        if "error" in recommendation:
             # Propagate the error message
            return schemas.ChatbotInteractionResponse(
                model_type=model_type,
                user_inputs=inputs,
                recommendation=recommendation, # Contains the error message
                justification=None,
                tips=None
            )

    except Exception as e: # Catch validation errors or other issues
        logger.error(f"Error processing chatbot interaction for {model_type}: {e}")
        recommendation = {"error": f"Failed to process request: {str(e)}"}


    return schemas.ChatbotInteractionResponse(
        model_type=model_type,
        user_inputs=inputs, # Return the original inputs for display
        recommendation=recommendation,
        justification=justification,
        tips=tips
    )
