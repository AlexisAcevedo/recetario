"""
User service - Business logic for user operations.
"""
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import UserNotFoundException, UserAlreadyExistsException


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get a list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user.
    
    Raises:
        UserAlreadyExistsException: If email already exists
    """
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise UserAlreadyExistsException()
    
    # Create user with hashed password
    user = User(
        email=user_data.email,
        password=get_password_hash(user_data.password),
        name=user_data.name,
        lastname=user_data.lastname
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsException()


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """
    Update an existing user.
    
    Raises:
        UserNotFoundException: If user doesn't exist
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()
    
    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Hash password if being updated
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user.
    
    Raises:
        UserNotFoundException: If user doesn't exist
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()
    
    db.delete(user)
    db.commit()
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Returns:
        User if credentials are valid, None otherwise
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
