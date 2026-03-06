"""
Tests para el sistema RBAC (Roles y Permisos) asíncronos.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.role import Role, Permission
from app.models.user import User
from app.core.security import get_password_hash


@pytest_asyncio.fixture
async def admin_role(db: AsyncSession) -> Role:
    """Crea rol admin con todos los permisos (Async)."""
    manage_users = Permission(name="manage_users", description="Gestionar usuarios")
    manage_roles = Permission(name="manage_roles", description="Gestionar roles")
    db.add_all([manage_users, manage_roles])
    await db.commit()
    
    role = Role(
        name="admin",
        description="Administrador del sistema",
        permissions=[manage_users, manage_roles]
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@pytest_asyncio.fixture
async def user_role(db: AsyncSession) -> Role:
    """Crea rol de usuario básico (Async)."""
    role = Role(name="user", description="Usuario básico")
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession, admin_role: Role) -> User:
    """Crea usuario administrador (Async)."""
    user = User(
        email="admin@example.com",
        password=get_password_hash("AdminPass123!@#"),
        name="Admin",
        lastname="User",
        role_id=admin_role.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, admin_user: User) -> dict:
    """Headers de autenticación para admin (Async)."""
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "admin@example.com", "password": "AdminPass123!@#"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
class TestRoleModel:
    """Tests del modelo Role (Async)."""
    
    async def test_role_creation(self, db: AsyncSession, admin_role: Role):
        """Verifica creación de rol con permisos."""
        assert admin_role.name == "admin"
        assert len(admin_role.permissions) == 2
    
    async def test_has_permission(self, admin_role: Role):
        """Verifica método has_permission."""
        assert admin_role.has_permission("manage_users") is True
        assert admin_role.has_permission("nonexistent") is False


@pytest.mark.asyncio
class TestUserWithRole:
    """Tests de usuario con rol (Async)."""
    
    async def test_user_role_assignment(self, admin_user: User, admin_role: Role):
        """Verifica asignación de rol a usuario."""
        assert admin_user.role is not None
        assert admin_user.role.name == "admin"
    
    async def test_user_has_permission(self, admin_user: User):
        """Verifica que usuario hereda permisos de rol."""
        assert admin_user.has_permission("manage_users") is True
        assert admin_user.has_permission("unknown_permission") is False
    
    async def test_user_without_role(self, db: AsyncSession):
        """Usuario sin rol no tiene permisos."""
        user = User(
            email="norole@example.com",
            password=get_password_hash("password"),
            name="No",
            lastname="Role"
        )
        db.add(user)
        await db.commit()
        
        assert user.role is None
        assert user.has_permission("anything") is False


@pytest.mark.asyncio
class TestRolesEndpoint:
    """Tests de endpoints de roles (Async)."""
    
    async def test_list_roles_requires_admin(self, client: AsyncClient, auth_headers: dict):
        """Usuario normal no puede listar roles."""
        response = await client.get("/api/v1/roles/", headers=auth_headers)
        assert response.status_code == 403
    
    async def test_list_roles_as_admin(
        self, client: AsyncClient, admin_headers: dict, admin_role: Role
    ):
        """Admin puede listar roles."""
        response = await client.get("/api/v1/roles/", headers=admin_headers)
        assert response.status_code == 200
        roles = response.json()
        assert len(roles) >= 1
        assert any(r["name"] == "admin" for r in roles)
    
    async def test_create_role_as_admin(self, client: AsyncClient, admin_headers: dict):
        """Admin puede crear roles."""
        response = await client.post(
            "/api/v1/roles/",
            headers=admin_headers,
            json={"name": "moderator", "description": "Moderador"}
        )
        assert response.status_code == 201
        assert response.json()["name"] == "moderator"
    
    async def test_assign_role_to_user(
        self,
        client: AsyncClient,
        admin_headers: dict,
        db: AsyncSession,
        user_role: Role
    ):
        """Admin puede asignar rol a usuario."""
        # Crear usuario sin rol
        user = User(
            email="newuser@example.com",
            password=get_password_hash("password"),
            name="New",
            lastname="User"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Asignar rol
        response = await client.post(
            "/api/v1/roles/assign",
            headers=admin_headers,
            json={"user_id": user.id, "role_id": user_role.id}
        )
        assert response.status_code == 200
        
        # Verificar
        await db.refresh(user)
        assert user.role_id == user_role.id


@pytest.mark.asyncio
class TestRequirePermission:
    """Tests de la dependencia require_permission (Async)."""
    
    async def test_user_without_permission_denied(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Usuario sin permiso específico es rechazado."""
        response = await client.get("/api/v1/roles/", headers=auth_headers)
        assert response.status_code == 403
