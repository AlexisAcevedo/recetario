from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import get_db
from schemas import UserSchema, TokenData
from jwt import get_current_user
import userService
from login_router import get_password_hash

router = APIRouter()


@router.get("", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Obtiene lista de usuarios (requiere autenticación)."""
    users = userService.get_user(db, skip, limit)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay usuarios"
        )
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Obtiene un usuario por ID."""
    user = userService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario inexistente"
        )
    return user


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def create_user(request: UserSchema, db: Session = Depends(get_db)):
    """Crea un nuevo usuario."""
    # Hash de la contraseña antes de guardar
    request.password = get_password_hash(request.password)
    return userService.create_user(db=db, user=request)