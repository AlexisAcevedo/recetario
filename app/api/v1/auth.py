"""
Router de Autenticación asíncrono.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.api import deps
from app.schemas.token import Token
from app.schemas.session import RefreshTokenRequest
from app.services import user_service
from app.core.limiter import limiter
from app.core.metrics import record_login_success, record_login_failed, record_token_refresh
from app.models.user import User

router = APIRouter()


@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """Login OAuth2 compatible (Async)."""
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        record_login_failed(reason="invalid_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = await security.create_session_with_tokens(
        db, user.id, ip_address=request.client.host if request.client else None
    )
    record_login_success(method="password")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(deps.get_db)
) -> Token:
    """Renueva un access token usando un refresh token (Async)."""
    new_tokens = await security.refresh_access_token(db, token_request.refresh_token)
    if not new_tokens:
        record_token_refresh(status="failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )

    record_token_refresh(status="success")
    access_token, refresh_token = new_tokens
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> None:
    """Cierra la sesión actual revocando todas las sesiones del usuario."""
    await security.revoke_all_sessions(db, current_user.id)
