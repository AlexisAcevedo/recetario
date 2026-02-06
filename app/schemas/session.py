"""
Esquemas Pydantic de Sesión.
Define modelos para refresh tokens y gestión de sesiones.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    """Esquema de respuesta de sesión."""
    id: int
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    expires_at: datetime
    is_current: bool = False  # Indica si es la sesión actual
    
    model_config = ConfigDict(from_attributes=True)


class TokenPair(BaseModel):
    """Par de tokens (access + refresh)."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request para renovar access token."""
    refresh_token: str
