"""
Authentication router - Login and token endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.token import Token
from app.services import user_service
from app.core.security import create_access_token
from app.core.exceptions import InvalidCredentialsException

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    OAuth2 compatible token login.
    
    - **username**: User email
    - **password**: User password
    
    Returns a JWT access token.
    """
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise InvalidCredentialsException()
    
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "name": user.name,
            "lastname": user.lastname
        }
    )
    
    return Token(access_token=access_token)
