"""
Utilidades de seguridad para autenticación asíncrona.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
import bcrypt
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash (Síncrono - CPU bound)."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt (Síncrono - CPU bound)."""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT de acceso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Decodifica y valida un token JWT."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


async def create_session_with_tokens(
    db: AsyncSession,
    user_id: int,
    device_info: Optional[str] = None,
    ip_address: Optional[str] = None
) -> tuple[str, str]:
    """Crea una sesión y genera tokens (Async)."""
    from app.models.session import Session, generate_refresh_token
    
    refresh_token = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    
    session = Session(
        user_id=user_id,
        refresh_token=refresh_token,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=expires_at
    )
    db.add(session)
    await db.commit()
    
    access_token = create_access_token(data={"user_id": user_id})
    return access_token, refresh_token


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Optional[tuple[str, str]]:
    """Renueva un access token (Async)."""
    from app.models.session import Session
    
    result = await db.execute(select(Session).filter(Session.refresh_token == refresh_token))
    session = result.scalar_one_or_none()
    
    if not session or not session.is_valid():
        return None
    
    session.last_used_at = datetime.now(timezone.utc)
    await db.commit()
    
    access_token = create_access_token(data={"user_id": session.user_id})
    return access_token, session.refresh_token


async def revoke_session(db: AsyncSession, session_id: int, user_id: int) -> bool:
    """Revoca una sesión específica (Async)."""
    from app.models.session import Session
    
    result = await db.execute(
        select(Session).filter(
            Session.id == session_id,
            Session.user_id == user_id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return False
    
    session.is_revoked = True
    await db.commit()
    return True


async def revoke_all_sessions(db: AsyncSession, user_id: int) -> int:
    """Revoca todas las sesiones de un usuario (Async)."""
    from app.models.session import Session
    
    result = await db.execute(
        update(Session)
        .filter(Session.user_id == user_id, Session.is_revoked == False)
        .values(is_revoked=True)
    )
    await db.commit()
    return result.rowcount
