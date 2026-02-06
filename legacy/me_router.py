from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import get_db
from schemas import UserSchema, TokenData
from jwt import get_current_user
import userService
from login_router import get_password_hash

router = APIRouter()


@router.get("", response_model=UserSchema)
async def get_me(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Obtiene datos del usuario autenticado."""
    user = userService.get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario inexistente"
        )
    return user


@router.put("", response_model=UserSchema)
async def update_me(
    request: UserSchema,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Actualiza datos del usuario autenticado."""
    password = request.password
    if password:
        password = get_password_hash(password)
    
    return userService.update_user(
        db=db,
        user_id=current_user.id,
        email=request.email or current_user.email,
        password=password,
        name=request.name or current_user.name,
        lastname=request.lastname or current_user.lastname
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Elimina la cuenta del usuario autenticado."""
    userService.delete_user(db=db, user_id=current_user.id)
    return None