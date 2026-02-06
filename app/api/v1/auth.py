"""
Router de Autenticación.
Endpoints para login, refresh y obtención de tokens.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.token import Token
from app.schemas.session import RefreshTokenRequest
from app.services import user_service
from app.core.security import create_session_with_tokens, refresh_access_token
from app.core.exceptions import InvalidCredentialsException
from app.core.limiter import limiter

router = APIRouter()


@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    Login compatible con OAuth2 para obtener tokens de acceso y refresh.
    
    Args:
        request: Request HTTP para obtener IP y device info
        form_data: Formulario con username (email) y password
        db: Sesión de base de datos
        
    Returns:
        Par de tokens (access + refresh)
        
    Raises:
        InvalidCredentialsException: Si las credenciales son inválidas
    """
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise InvalidCredentialsException()
    
    # Obtener info del cliente
    device_info = request.headers.get("User-Agent", "Unknown")
    ip_address = request.client.host if request.client else None
    
    # Crear sesión y obtener tokens
    access_token, refresh_token = create_session_with_tokens(
        db=db,
        user_id=user.id,
        device_info=device_info,
        ip_address=ip_address
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Token:
    """
    Renueva el access token usando un refresh token válido.
    
    Args:
        token_request: Request con el refresh token
        db: Sesión de base de datos
        
    Returns:
        Nuevo access token
        
    Raises:
        InvalidCredentialsException: Si el refresh token es inválido o expirado
    """
    result = refresh_access_token(db, token_request.refresh_token)
    
    if not result:
        raise InvalidCredentialsException(detail="Refresh token inválido o expirado")
    
    access_token, _ = result
    return Token(access_token=access_token)
