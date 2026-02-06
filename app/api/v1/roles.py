"""
Router de Roles y Permisos.
Endpoints administrativos para gestión RBAC.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_cache.decorator import cache

from app.api.deps import get_db, require_role
from app.models.role import Role, Permission
from app.models.user import User
from app.schemas.role import (
    RoleCreate, RoleResponse, RoleUpdate,
    PermissionResponse, RoleAssign
)

router = APIRouter()


@router.get("/", response_model=List[RoleResponse])
@cache(expire=3600)
async def list_roles(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
) -> List[Role]:
    """
    Lista todos los roles disponibles.
    
    Requiere rol: admin
    """
    return db.query(Role).all()


@router.get("/permissions", response_model=List[PermissionResponse])
@cache(expire=86400) # Permisos cambian muy poco
async def list_permissions(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
) -> List[Permission]:
    """
    Lista todos los permisos disponibles.
    
    Requiere rol: admin
    """
    return db.query(Permission).all()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
) -> Role:
    """
    Crea un nuevo rol.
    
    Requiere rol: admin
    """
    # Verificar nombre único
    if db.query(Role).filter(Role.name == role_data.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un rol con ese nombre"
        )
    
    # Crear rol
    role = Role(name=role_data.name, description=role_data.description)
    
    # Asignar permisos si se proporcionaron
    if role_data.permission_ids:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_data.permission_ids)
        ).all()
        role.permissions = permissions
    
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
) -> Role:
    """
    Actualiza un rol existente.
    
    Requiere rol: admin
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Actualizar campos proporcionados
    if role_data.name is not None:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.permission_ids is not None:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_data.permission_ids)
        ).all()
        role.permissions = permissions
    
    db.commit()
    db.refresh(role)
    return role


@router.post("/assign", response_model=dict)
async def assign_role_to_user(
    assignment: RoleAssign,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
) -> dict:
    """
    Asigna un rol a un usuario.
    
    Requiere rol: admin
    """
    # Verificar usuario
    user = db.query(User).filter(User.id == assignment.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar rol
    role = db.query(Role).filter(Role.id == assignment.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Asignar
    user.role_id = role.id
    db.commit()
    
    return {"message": f"Rol '{role.name}' asignado a usuario '{user.email}'"}


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
):
    """
    Elimina un rol.
    
    Requiere rol: admin
    No se pueden eliminar roles con usuarios asignados.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Verificar que no tenga usuarios
    if role.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un rol con usuarios asignados"
        )
    
    db.delete(role)
    db.commit()
