"""
Modelo SQLAlchemy de Usuario.
Define la estructura de la tabla users en la base de datos.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """
    Modelo de usuario para la base de datos.
    
    Atributos:
        id: Identificador único (clave primaria)
        email: Correo electrónico (único, indexado)
        password: Contraseña hasheada con bcrypt
        name: Nombre del usuario
        lastname: Apellido del usuario
        role_id: FK al rol asignado (default: rol 'user')
        created_at: Fecha de creación (automática)
        updated_at: Fecha de última actualización (automática)
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con Role
    role = relationship("Role", back_populates="users")
    
    def has_permission(self, permission_name: str) -> bool:
        """Verifica si el usuario tiene un permiso específico."""
        if self.role is None:
            return False
        return self.role.has_permission(permission_name)
    
    def __repr__(self) -> str:
        """Representación legible del usuario."""
        return f"<User {self.email}>"

