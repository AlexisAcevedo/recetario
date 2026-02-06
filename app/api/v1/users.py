"""
Router de Usuarios.
Endpoints CRUD para gestión de usuarios.
"""
from typing import List

from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.models.user import User
from app.core.limiter import limiter

router = APIRouter()


@router.get("", response_model=List[UserResponse])
@limiter.limit("100/minute")
async def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[UserResponse]:
    """
    Obtiene todos los usuarios (requiere autenticación).
    
    Args:
        request: Request con IP para rate limiting
        skip: Número de usuarios a omitir (paginación)
        limit: Máximo de usuarios a retornar
        
    Returns:
        Lista de usuarios
    """
    return user_service.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
@limiter.limit("100/minute")
async def get_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Obtiene un usuario por su ID.
    
    Args:
        request: Request con IP para rate limiting
        user_id: ID del usuario a buscar
        
    Returns:
        Datos del usuario
        
    Raises:
        404: Si el usuario no existe
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        from app.core.exceptions import UserNotFoundException
        raise UserNotFoundException()
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def create_user(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Crea un nuevo usuario.
    
    Args:
        request: Request con IP para rate limiting
        user_data: Datos del usuario a crear
        
    Returns:
        Usuario creado
        
    Raises:
        400: Si el email ya está registrado
    """
    return user_service.create_user(db, user_data)
