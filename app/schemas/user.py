"""
Esquemas Pydantic de Usuario.
Define los modelos para validación de requests y responses.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Esquema base con campos comunes de usuario."""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    lastname: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """
    Esquema para crear un nuevo usuario.
    
    Extiende UserBase agregando el campo password.
    """
    password: str = Field(..., min_length=8, description="Mínimo 8 caracteres")


class UserUpdate(BaseModel):
    """
    Esquema para actualizar datos de usuario.
    
    Todos los campos son opcionales - solo se actualizan los proporcionados.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    lastname: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=8)


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
