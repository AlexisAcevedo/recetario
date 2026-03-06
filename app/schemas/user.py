"""
Esquemas Pydantic de Usuario.
Define los modelos para validación de requests y responses.
"""
from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


# Blacklist centralizada de contraseñas comunes
_COMMON_PASSWORDS = {
    'password', 'password123', '12345678', '123456789', '1234567890',
    'qwertyuiop', 'abc123', 'password1', 'admin123', 'letmein',
    'welcome', 'monkey', 'dragon', '111111', 'qwerty123',
    'password123!', 'password123!@#', 'admin123456!', 'qwerty123456!',
    'p@ssw0rd1234', 'welcome12345!', 'changeme1234!'
}


def _validate_password_strength(password: str) -> str:
    """Validación centralizada de contraseñas según NIST SP 800-63B."""
    if not re.search(r'[A-Z]', password):
        raise ValueError('Debe contener al menos una mayúscula')
    if not re.search(r'[a-z]', password):
        raise ValueError('Debe contener al menos una minúscula')
    if not re.search(r'[0-9]', password):
        raise ValueError('Debe contener al menos un número')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError('Debe contener al menos un símbolo especial (!@#$%^&*...)')
    if password.lower() in _COMMON_PASSWORDS:
        raise ValueError('Contraseña demasiado común. Por favor, elige una más segura.')
    return password


class UserBase(BaseModel):
    """Esquema base con campos comunes de usuario."""
    email: EmailStr = Field(..., max_length=254)
    name: str = Field(..., min_length=2, max_length=100)
    lastname: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """
    Esquema para crear un nuevo usuario.

    Extiende UserBase agregando el campo password con validación fuerte.
    """
    password: str = Field(
        ...,
        min_length=12,
        description="Mínimo 12 caracteres, debe incluir mayúsculas, minúsculas, números y símbolos especiales"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)


class UserUpdate(BaseModel):
    """
    Esquema para actualizar datos de usuario.

    Todos los campos son opcionales - solo se actualizan los proporcionados.
    """
    email: Optional[EmailStr] = Field(None, max_length=254)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    lastname: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=12)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_password_strength(v)


class UserResponse(UserBase):
    """
    Esquema para respuestas de usuario.
    
    Excluye la contraseña por seguridad.
    Incluye timestamps de creación y actualización.
    """
    id: int
    role: Optional[str] = None  # Nombre del rol asignado
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_user(cls, user) -> "UserResponse":
        """Crea respuesta desde modelo User incluyendo nombre del rol."""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            lastname=user.lastname,
            role=user.role.name if user.role else None,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


class UserInDB(UserResponse):
    """
    Esquema de usuario con contraseña hasheada.
    
    Solo para uso interno - nunca retornar en responses.
    """
    password: str
