"""
Router de Usuarios.
Endpoints CRUD para gestión de usuarios.
"""
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[UserResponse]:
    """
    Obtiene todos los usuarios (requiere autenticación).
    
    Args:
        skip: Número de usuarios a omitir (paginación)
        limit: Máximo de usuarios a retornar
        
    Returns:
        Lista de usuarios
    """
    return user_service.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Obtiene un usuario por su ID.
    
    Args:
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
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Crea un nuevo usuario.
    
    Args:
        user_data: Datos del usuario a crear
        
    Returns:
        Usuario creado
        
    Raises:
        400: Si el email ya está registrado
    """
    return user_service.create_user(db, user_data)
