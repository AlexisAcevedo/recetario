"""
Router de Mi Perfil asíncrono.
"""
from fastapi import APIRouter, Depends, status, Request, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.session import SessionResponse
from app.services import user_service
from app.models.user import User
from app.core import security
from app.core.limiter import limiter

router = APIRouter()


@router.get("", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Obtiene el perfil del usuario actual."""
    return UserResponse.from_user(current_user)


@router.put("", response_model=UserResponse)
@limiter.limit("10/minute")
async def update_me(
    request: Request,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Actualiza el perfil del usuario actual (Async)."""
    updated = await user_service.update_user(db, current_user.id, user_data)
    return UserResponse.from_user(updated)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Elimina la cuenta del usuario actual (Async)."""
    await user_service.delete_user(db, current_user.id)


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[SessionResponse]:
    """Lista todas las sesiones activas del usuario (Async)."""
    return await user_service.get_user_sessions(db, current_user.id)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session_endpoint(
    session_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
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
) -> None:
    """Revoca TODAS las sesiones activas (Async)."""
    await security.revoke_all_sessions(db, current_user.id)
