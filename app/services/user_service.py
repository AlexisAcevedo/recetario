"""
Servicio de Usuario - Lógica de negocio asíncrona para operaciones de usuarios.
"""
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.session import Session as SessionModel
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import (
    async_get_password_hash, async_verify_password,
    get_password_hash, verify_password,
)
from app.core.exceptions import UserNotFoundException, UserAlreadyExistsException
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Obtiene un usuario por su ID (Async)."""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Obtiene un usuario por su email (Async)."""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Obtiene una lista de usuarios con paginación (Async)."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def count_users(db: AsyncSession) -> int:
    """Cuenta el total de usuarios (Async)."""
    result = await db.execute(select(func.count(User.id)))
    return result.scalar() or 0


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Crea un nuevo usuario con mitigación de timing attacks (Async)."""
    # SIEMPRE hashear para timing consistency (bcrypt ~200ms, en thread pool)
    hashed_password = await async_get_password_hash(user_data.password)

    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        logger.warning("user_creation_duplicate_email", email=user_data.email)
        raise UserAlreadyExistsException()

    user = User(
        email=user_data.email,
        password=hashed_password,
        name=user_data.name,
        lastname=user_data.lastname
    )

    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("user_created", user_id=user.id, email=user.email)
        return user
    except IntegrityError:
        await db.rollback()
        raise UserAlreadyExistsException()


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
    """Actualiza un usuario existente (Async)."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()

    update_data = user_data.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["password"] = await async_get_password_hash(update_data["password"])

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    logger.info("user_updated", user_id=user_id)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Elimina un usuario (Async)."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()

    await db.delete(user)
    await db.commit()
    logger.info("user_deleted", user_id=user_id)
    return True


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Autentica un usuario (Async). Usa thread pool para bcrypt."""
    user = await get_user_by_email(db, email)
    if not user:
        # Timing attack mitigation: hash+verify dummy en thread pool
        dummy_hash = await async_get_password_hash("dummy_password")
        await async_verify_password("dummy_password", dummy_hash)
        logger.warning("auth_failed_user_not_found", email=email)
        return None
    if not await async_verify_password(password, user.password):
        logger.warning("auth_failed_wrong_password", user_id=user.id)
        return None
    logger.info("auth_success", user_id=user.id)
    return user


async def get_user_sessions(
    db: AsyncSession, user_id: int, active_only: bool = True
) -> List[SessionModel]:
    """Obtiene las sesiones de un usuario."""
    query = select(SessionModel).filter(SessionModel.user_id == user_id)
    if active_only:
        query = query.filter(SessionModel.is_revoked == False)
    result = await db.execute(query)
    return result.scalars().all()
