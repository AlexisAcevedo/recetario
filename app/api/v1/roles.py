"""
Router de Roles y Permisos asíncrono.
Endpoints para gestión del sistema RBAC.
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi_cache.decorator import cache

from app.api.deps import get_db, require_role
from app.schemas.role import RoleResponse, RoleCreate, RoleAssign
from app.models.role import Role, Permission
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=list[RoleResponse])
@cache(expire=60)
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
) -> list[RoleResponse]:
    """
    Lista todos los roles disponibles (Async).
    
    Requiere rol: admin
    """
    result = await db.execute(select(Role))
    return result.scalars().all()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
) -> Role:
    """
    Crea un nuevo rol (Async).
    
    Requiere rol: admin
    """
    # Verificar nombre único
    result = await db.execute(select(Role).filter(Role.name == role_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El rol '{role_data.name}' ya existe"
        )
    
    # Crear rol
    role = Role(
        name=role_data.name,
        description=role_data.description
    )
    
    # Asignar permisos si se proporcionan
    if role_data.permission_ids:
        res_perms = await db.execute(
            select(Permission).filter(Permission.id.in_(role_data.permission_ids))
        )
        role.permissions = res_perms.scalars().all()
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.post("/assign", response_model=dict)
async def assign_role_to_user(
    assignment: RoleAssign,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(["admin"]))
) -> dict:
    """
    Asigna un rol a un usuario (Async).
    
    Requiere rol: admin
    """
    # Verificar usuario
    res_user = await db.execute(select(User).filter(User.id == assignment.user_id))
    user = res_user.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar rol
    res_role = await db.execute(select(Role).filter(Role.id == assignment.role_id))
    role = res_role.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Asignar
    user.role_id = role.id
    await db.commit()
    
    return {"message": f"Rol '{role.name}' asignado a usuario '{user.email}'"}
