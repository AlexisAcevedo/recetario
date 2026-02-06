"""
Dependencias de la API.
Funciones reutilizables para inyección de dependencias en endpoints.
"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.core.exceptions import NotAuthenticatedException
from app.models.user import User
from app.schemas.token import TokenData

# Esquema OAuth2 para autenticación con token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_db() -> Generator:
    """
    Proporciona una sesión de base de datos.
    
    Se usa como dependencia de FastAPI para inyectar
    la sesión en los endpoints automáticamente.
    
    Yields:
        Session: Sesión de SQLAlchemy
    """
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
    Obtiene el usuario actual autenticado desde el token JWT.
    
    Args:
        token: Token JWT del header Authorization
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        NotAuthenticatedException: Si el token es inválido o el usuario no existe
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
    Obtiene el usuario actual si está autenticado, None en caso contrario.
    
    Útil para endpoints que funcionan con o sin autenticación.
    
    Returns:
        Usuario autenticado o None
    """
    try:
        return get_current_user(token, db)
    except (HTTPException, JWTError):
        return None


def require_role(allowed_roles: list[str]):
    """
    Dependencia que verifica si el usuario tiene uno de los roles permitidos.
    
    Args:
        allowed_roles: Lista de nombres de roles permitidos
        
    Raises:
        HTTPException 403: Si el usuario no tiene el rol requerido
        
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
    
    Args:
        permission_name: Nombre del permiso requerido
        
    Raises:
        HTTPException 403: Si el usuario no tiene el permiso
        
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

