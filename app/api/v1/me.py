"""
Me router - Current user profile endpoints.
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
    Get current user profile.
    """
    return current_user


@router.put("", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Update current user profile.
    
    All fields are optional - only provided fields will be updated.
    """
    return user_service.update_user(db, current_user.id, user_data)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete current user account.
    
    ⚠️ This action is irreversible!
    """
    user_service.delete_user(db, current_user.id)
    return None
