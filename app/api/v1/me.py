"""
Router de Mi Perfil asíncrono.
"""
from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.session import SessionResponse
from app.services import user_service
from app.models.user import User
from app.models.session import Session as SessionModel
from app.core import security

router = APIRouter()


@router.get("", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Obtiene el perfil del usuario actual."""
    return current_user


@router.put("", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Actualiza el perfil del usuario actual (Async)."""
    return await user_service.update_user(db, current_user.id, user_data)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Elimina la cuenta del usuario actual (Async)."""
    await user_service.delete_user(db, current_user.id)
    return None


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[SessionResponse]:
    """Lista todas las sesiones activas del usuario (Async)."""
    result = await db.execute(
        select(SessionModel).filter(
            SessionModel.user_id == current_user.id,
            SessionModel.is_revoked == False
        )
    )
    return result.scalars().all()


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session_endpoint(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoca una sesión específica (Async)."""
    success = await security.revoke_session(db, session_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )


@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_all_sessions_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoca TODAS las sesiones activas (Async)."""
    await security.revoke_all_sessions(db, current_user.id)
