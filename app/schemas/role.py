"""
Esquemas Pydantic de Rol y Permiso.
Define los modelos para validación en el sistema RBAC.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class PermissionBase(BaseModel):
    """Esquema base de permiso."""
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class PermissionCreate(PermissionBase):
    """Esquema para crear un permiso."""
    pass


class PermissionResponse(PermissionBase):
    """Esquema de respuesta de permiso."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class RoleBase(BaseModel):
    """Esquema base de rol."""
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class RoleCreate(RoleBase):
    """Esquema para crear un rol."""
    permission_ids: List[int] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    """Esquema para actualizar un rol."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """Esquema de respuesta de rol."""
    id: int
    permissions: List[PermissionResponse] = []
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class RoleAssign(BaseModel):
    """Esquema para asignar rol a usuario."""
    user_id: int
    role_id: int
