"""
Modelos SQLAlchemy de Rol y Permiso.
Define las estructuras para el sistema RBAC (Role-Based Access Control).
"""
from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# Tabla de asociación roles-permisos (many-to-many)
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


class Permission(Base):
    """
    Modelo de permiso para control de acceso granular.
    
    Atributos:
        id: Identificador único
        name: Nombre del permiso (ej: 'create_recipe', 'manage_users')
        description: Descripción legible del permiso
    """
    
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Permission {self.name}>"


class Role(Base):
    """
    Modelo de rol para agrupación de permisos.
    
    Atributos:
        id: Identificador único
        name: Nombre del rol (ej: 'user', 'moderator', 'admin')
        description: Descripción del rol
        permissions: Lista de permisos asociados
        created_at: Fecha de creación
    """
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación many-to-many con permisos
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        backref="roles"
    )
    
    # Relación con usuarios
    users = relationship("User", back_populates="role")
    
    def has_permission(self, permission_name: str) -> bool:
        """Verifica si el rol tiene un permiso específico."""
        return any(p.name == permission_name for p in self.permissions)
    
    def __repr__(self) -> str:
        return f"<Role {self.name}>"
