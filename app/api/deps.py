"""
Dependencias de la API.
Funciones reutilizables para inyección de dependencias en endpoints.
"""
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.database import AsyncSessionLocal
from app.core.security import decode_token, validate_session
from app.core.exceptions import NotAuthenticatedException
from app.models.user import User

# Esquema OAuth2 para autenticación con token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


async def get_db() -> AsyncGenerator:
    """Proporciona una sesión de base de datos asíncrona."""
    async with AsyncSessionLocal() as db:
        yield db


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Obtiene el usuario actual autenticado (Asíncrono).
    Valida que el token JWT sea válido y que la sesión asociada esté activa.
    """
    payload = decode_token(token)

    if payload is None:
        raise NotAuthenticatedException()

    user_id: int = payload.get("user_id")
    if user_id is None:
        raise NotAuthenticatedException()

    # Validar sesión activa si el token incluye session_id
    session_id: Optional[int] = payload.get("session_id")
    if session_id is not None:
        is_valid = await validate_session(db, session_id, user_id)
        if not is_valid:
            raise NotAuthenticatedException(detail="Sesión revocada o expirada")

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotAuthenticatedException()

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Obtiene el usuario actual si está autenticado, None en caso contrario.
    Útil para endpoints que funcionan con o sin autenticación.
    """
    if token is None:
        return None
    try:
        return await get_current_user(token, db)
    except NotAuthenticatedException:
        return None


def require_role(allowed_roles: list[str]):
    """
    Dependencia que verifica si el usuario tiene uno de los roles permitidos.

    Uso:
        @router.get("/admin", dependencies=[Depends(require_role(["admin"]))])
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sin rol asignado"
            )
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol '{current_user.role.name}' no tiene acceso a este recurso"
            )
        return current_user
    return role_checker


def require_permission(permission_name: str):
    """
    Dependencia que verifica si el usuario tiene un permiso específico.

    Uso:
        @router.delete("/recipe/{id}", dependencies=[Depends(require_permission("delete_recipe"))])
    """
    def permission_checker(current_user: User = Depends(get_current_user)):
        if not current_user.has_permission(permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso '{permission_name}' requerido"
            )
        return current_user
    return permission_checker

