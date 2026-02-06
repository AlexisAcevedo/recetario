"""
API Dependencies - Reusable dependency functions.
"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.core.exceptions import NotAuthenticatedException
from app.models.user import User
from app.schemas.token import TokenData

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_db() -> Generator:
    """Provide database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Raises:
        NotAuthenticatedException: If token is invalid or user not found
    """
    payload = decode_token(token)
    
    if payload is None:
        raise NotAuthenticatedException()
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise NotAuthenticatedException()
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise NotAuthenticatedException()
    
    return user


def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Get the current user if authenticated, None otherwise.
    Useful for endpoints that work with or without authentication.
    """
    try:
        return get_current_user(token, db)
    except:
        return None
