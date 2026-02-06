"""
Utilidades de seguridad para autenticación.
Maneja el hasheo de contraseñas y operaciones con tokens JWT.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
import bcrypt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash bcrypt almacenado
        
    Returns:
        True si las contraseñas coinciden, False en caso contrario
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """
    Genera un hash bcrypt para una contraseña.
    
    Args:
        password: Contraseña a hashear
        
    Returns:
        Hash bcrypt de la contraseña
        
    Nota:
        bcrypt tiene un límite de 72 bytes. Las contraseñas más largas
        se truncan automáticamente por seguridad.
    """
    # Truncar a 72 bytes (límite de bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.
    
    Args:
        data: Datos a incluir en el payload del token
        expires_delta: Tiempo de expiración personalizado (opcional)
        
    Returns:
        Token JWT codificado como string
    """
    to_encode = data.copy()
    
    # Calcular tiempo de expiración
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    
    # Codificar y retornar el token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un token JWT.
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Payload del token si es válido, None si es inválido o expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def create_session_with_tokens(
    db,  # Session de SQLAlchemy
    user_id: int,
    device_info: Optional[str] = None,
    ip_address: Optional[str] = None
) -> tuple[str, str]:
    """
    Crea una sesión y genera par de tokens (access + refresh).
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        device_info: Información del dispositivo/navegador
        ip_address: IP del cliente
        
    Returns:
        Tupla (access_token, refresh_token)
    """
    from app.models.session import Session, generate_refresh_token
    
    # Generar refresh token
    refresh_token = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    
    # Crear sesión en DB
    session = Session(
        user_id=user_id,
        refresh_token=refresh_token,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    
    # Generar access token
    access_token = create_access_token(data={"user_id": user_id})
    
    return access_token, refresh_token


def refresh_access_token(db, refresh_token: str) -> Optional[tuple[str, "Session"]]:
    """
    Renueva un access token usando un refresh token válido.
    
    Args:
        db: Sesión de base de datos
        refresh_token: Token de refresh
        
    Returns:
        Tupla (nuevo_access_token, session) o None si inválido
    """
    from app.models.session import Session
    
    session = db.query(Session).filter(
        Session.refresh_token == refresh_token
    ).first()
    
    if not session or not session.is_valid():
        return None
    
    # Actualizar última vez usado
    session.last_used_at = datetime.now(timezone.utc)
    db.commit()
    
    # Generar nuevo access token
    access_token = create_access_token(data={"user_id": session.user_id})
    
    return access_token, session


def revoke_session(db, session_id: int, user_id: int) -> bool:
    """
    Revoca una sesión específica de un usuario.
    
    Args:
        db: Sesión de base de datos
        session_id: ID de la sesión a revocar
        user_id: ID del usuario (para verificar propiedad)
        
    Returns:
        True si se revocó, False si no se encontró o no pertenece al usuario
    """
    from app.models.session import Session
    
    session = db.query(Session).filter(
        Session.id == session_id,
        Session.user_id == user_id
    ).first()
    
    if not session:
        return False
    
    session.is_revoked = True
    db.commit()
    return True


def revoke_all_sessions(db, user_id: int) -> int:
    """
    Revoca todas las sesiones de un usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Número de sesiones revocadas
    """
    from app.models.session import Session
    
    count = db.query(Session).filter(
        Session.user_id == user_id,
        Session.is_revoked == False
    ).update({"is_revoked": True})
    db.commit()
    return count

