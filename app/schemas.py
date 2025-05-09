from pydantic import BaseModel, EmailStr, field_validator, model_validator, ValidationInfo
from typing import Optional, Dict, Any, List
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    confirm_password: Optional[str] = None # For signup form

    @model_validator(mode='after')
    def passwords_match(self) -> 'UserCreate':
        if self.password is not None and self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        # Ensure confirm_password is not passed to the User model if it's just for validation
        # However, our User model doesn't have confirm_password, so it's fine.
        return self

class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- UserDataInput Schemas ---
class UserDataInputBase(BaseModel):
    model_type: str
    input_data: Dict[str, Any]

class UserDataInputCreate(UserDataInputBase):
    pass

class UserDataInputResponse(UserDataInputBase):
    id: int
    user_id: int
    timestamp: datetime
    # output_data: Optional[Dict[str, Any]] = None # If storing output

    class Config:
        from_attributes = True

class UserWithInputs(User):
    inputs: List[UserDataInputResponse] = []

    class Config: # Added for consistency, though User already has it.
        from_attributes = True


# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# --- Chatbot Input Schemas (Specific to each model for validation) ---
# These can be more specific if needed, for now using a generic Dict
# For example, for Base Model:
class BaseModeInputSchema(BaseModel):
    Salary: float
    Expenses: float
    Savings: float
    Lifecycle_Stage: str 
    Risk_Appetite: str
    Investment_Horizon: str

    @field_validator('Salary', 'Expenses', 'Savings')
    @classmethod
    def check_non_negative_numeric(cls, v: Any, info: ValidationInfo) -> Any:
        if not isinstance(v, (int, float)):
            raise ValueError(f"{info.field_name} must be a number")
        if v < 0:
            raise ValueError(f"{info.field_name} cannot be negative")
        return v
    
    class Config:
        from_attributes = True


class EnhancedModelInputSchema(BaseModel):
    Profession: str
    City: str
    Salary: float
    Expenses: float
    Savings: float
    Lifecycle_Stage: str
    Risk_Appetite: str
    Investment_Horizon: str

    @field_validator('Salary', 'Expenses', 'Savings')
    @classmethod
    def check_non_negative_numeric(cls, v: Any, info: ValidationInfo) -> Any:
        if not isinstance(v, (int, float)):
            raise ValueError(f"{info.field_name} must be a number")
        if v < 0:
            raise ValueError(f"{info.field_name} cannot be negative")
        return v

    class Config:
        from_attributes = True

class RuleBasedModelInputSchema(BaseModel):
    Lifecycle_Stage: str
    Risk_Appetite: str
    Investment_Horizon: str
    Annual_Salary_Package: float
    Monthly_In_hand_Salary: float
    Total_Monthly_Expenses: float

    @field_validator('Annual_Salary_Package', 'Monthly_In_hand_Salary', 'Total_Monthly_Expenses')
    @classmethod
    def check_non_negative_numeric(cls, v: Any, info: ValidationInfo) -> Any:
        if not isinstance(v, (int, float)):
            raise ValueError(f"{info.field_name} must be a number")
        if v < 0:
            raise ValueError(f"{info.field_name} cannot be negative")
        return v
    
    class Config:
        from_attributes = True

# For the chatbot interaction, the form will likely submit a dictionary.
# The specific schema can be used within the service layer before passing to the model.
class ChatbotInteractionRequest(BaseModel):
    model_type: str # "base", "enhanced", "rule_based"
    inputs: Dict[str, Any]

class ChatbotInteractionResponse(BaseModel):
    model_type: str
    user_inputs: Dict[str, Any]
    recommendation: Dict[str, Any] # e.g., portfolio allocation
    justification: Optional[List[str]] = None # For rule-based
    tips: Optional[List[str]] = None # For rule-based
