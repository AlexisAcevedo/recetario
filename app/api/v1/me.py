"""
Router de Mi Perfil.
Endpoints para gestión del perfil del usuario actual.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.services import user_service
from app.models.user import User

router = APIRouter()


@router.get("", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Obtiene el perfil del usuario actual.
    
    Returns:
        Datos del usuario autenticado
    """
    return current_user


@router.put("", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Actualiza el perfil del usuario actual.
    
    Todos los campos son opcionales - solo se actualizan los proporcionados.
    
    Returns:
        Usuario actualizado
    """
    return user_service.update_user(db, current_user.id, user_data)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Elimina la cuenta del usuario actual.
    
    ⚠️ Esta acción es irreversible.
    """
    user_service.delete_user(db, current_user.id)
    return None
