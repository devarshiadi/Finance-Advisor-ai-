from sqlalchemy.orm import Session
from . import models, schemas
from .core.security import get_password_hash
from typing import List, Optional

# --- User CRUD ---
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_admin_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, is_admin=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- UserDataInput CRUD ---
def create_user_data_input(db: Session, item: schemas.UserDataInputCreate, user_id: int) -> models.UserDataInput:
    db_item = models.UserDataInput(**item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_user_data_inputs_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.UserDataInput]:
    return db.query(models.UserDataInput).filter(models.UserDataInput.user_id == user_id).offset(skip).limit(limit).all()

def get_all_user_data_inputs(db: Session, skip: int = 0, limit: int = 1000) -> List[models.UserDataInput]:
    """
    Fetches all user data inputs, primarily for admin use.
    Consider pagination for very large datasets.
    """
    return db.query(models.UserDataInput).order_by(models.UserDataInput.timestamp.desc()).offset(skip).limit(limit).all()
