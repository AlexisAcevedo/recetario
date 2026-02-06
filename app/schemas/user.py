"""
Esquemas Pydantic de Usuario.
Define los modelos para validación de requests y responses.
"""
from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class UserBase(BaseModel):
    """Esquema base con campos comunes de usuario."""
    email: EmailStr
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
        """
        Valida que la contraseña cumpla con requisitos de seguridad.
        
        Requisitos:
        - Mínimo 12 caracteres (según NIST)
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        - Al menos un símbolo especial
        - No debe estar en lista de contraseñas comunes
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('Debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Debe contener al menos una minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Debe contener al menos un símbolo especial (!@#$%^&*...)')
        
        # Blacklist de contraseñas comunes
        common_passwords = [
            'password', 'password123', '12345678', '123456789', '1234567890',
            'qwertyuiop', 'abc123', 'password1', 'admin123', 'letmein',
            'welcome', 'monkey', 'Dragon', '111111', 'qwerty123'
        ]
        if v.lower() in [p.lower() for p in common_passwords]:
            raise ValueError('Contraseña demasiado común. Por favor, elige una más segura.')
        
        return v


class UserUpdate(BaseModel):
    """
    Esquema para actualizar datos de usuario.
    
    Todos los campos son opcionales - solo se actualizan los proporcionados.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    lastname: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=12)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Valida contraseña si se proporciona."""
        if v is None:
            return v
        
        # Misma validación que UserCreate
        if not re.search(r'[A-Z]', v):
            raise ValueError('Debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Debe contener al menos una minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Debe contener al menos un símbolo especial')
        
        common_passwords = [
            'password', 'password123', '12345678', '123456789', '1234567890',
            'qwertyuiop', 'abc123', 'password1', 'admin123', 'letmein'
        ]
        if v.lower() in [p.lower() for p in common_passwords]:
            raise ValueError('Contraseña demasiado común')
        
        return v


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
    def from_user(cls, user):
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
