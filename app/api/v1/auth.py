"""
Router de Autenticación asíncrono.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core import security
from app.core.config import settings
from app.api import deps
from app.schemas.token import Token
from app.schemas.session import RefreshTokenRequest
from app.services import user_service
from app.core.limiter import limiter

router = APIRouter()


@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    Login OAuth2 compatible (Async).
    """
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear tokens y sesión
    access_token, refresh_token = await security.create_session_with_tokens(db, user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(deps.get_db)
) -> Token:
    """
    Renueva un access token usando un refresh token (Async).
    """
    new_tokens = await security.refresh_access_token(db, token_request.refresh_token)
    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )
    
    access_token, refresh_token = new_tokens
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
