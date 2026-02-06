from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    """Esquema para operaciones con usuarios."""
    id: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    lastname: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Login(BaseModel):
    """Esquema para login."""
    email: str
    password: str


class Token(BaseModel):
    """Esquema para respuesta de token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Datos extraídos del token."""
    email: Optional[str] = None
    id: Optional[int] = None
    name: Optional[str] = None
    lastname: Optional[str] = None