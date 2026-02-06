"""
Modelo SQLAlchemy de Sesión.
Almacena refresh tokens y sesiones activas de usuarios.
"""
import secrets
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


def generate_refresh_token() -> str:
    """Genera un token de refresh seguro de 64 caracteres."""
    return secrets.token_urlsafe(48)


class Session(Base):
    """
    Modelo de sesión para refresh tokens.
    
    Atributos:
        id: Identificador único
        user_id: FK al usuario propietario
        refresh_token: Token único para renovar access token
        device_info: Información del dispositivo/navegador
        ip_address: IP desde donde se creó la sesión
        is_revoked: Si la sesión fue revocada manualmente
        expires_at: Fecha de expiración del refresh token
        created_at: Fecha de creación de la sesión
        last_used_at: Última vez que se usó para refrescar
    """
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    refresh_token = Column(String(100), unique=True, nullable=False, index=True)
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relación con User
    user = relationship("User", backref="sessions")
    
    def is_valid(self) -> bool:
        """Verifica si la sesión es válida (no expirada ni revocada)."""
        from datetime import datetime, timezone
        if self.is_revoked:
            return False
        if self.expires_at < datetime.now(timezone.utc):
            return False
        return True
    
    def __repr__(self) -> str:
        return f"<Session user_id={self.user_id} revoked={self.is_revoked}>"
