from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inputs = relationship("UserDataInput", back_populates="owner")

class UserDataInput(Base):
    __tablename__ = "user_data_inputs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_type = Column(String, index=True) # "base", "enhanced", "rule_based"
    input_data = Column(JSON) # Stores the dictionary of inputs
    # Output data can also be stored if needed, e.g., portfolio allocation
    # output_data = Column(JSON) 
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="inputs")
