"""
Tests para el sistema RBAC (Roles y Permisos).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.role import Role, Permission
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def admin_role(db: Session) -> Role:
    """Crea rol admin con todos los permisos."""
    # Crear permisos
    manage_users = Permission(name="manage_users", description="Gestionar usuarios")
    manage_roles = Permission(name="manage_roles", description="Gestionar roles")
    db.add_all([manage_users, manage_roles])
    db.commit()
    
    # Crear rol admin
    role = Role(
        name="admin",
        description="Administrador del sistema",
        permissions=[manage_users, manage_roles]
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@pytest.fixture
def user_role(db: Session) -> Role:
    """Crea rol de usuario básico."""
    role = Role(name="user", description="Usuario básico")
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@pytest.fixture
def admin_user(db: Session, admin_role: Role) -> User:
    """Crea usuario administrador."""
    user = User(
        email="admin@example.com",
        password=get_password_hash("AdminPass123!@#"),
        name="Admin",
        lastname="User",
        role_id=admin_role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_headers(client: TestClient, admin_user: User) -> dict:
    """Headers de autenticación para admin."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin@example.com", "password": "AdminPass123!@#"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestRoleModel:
    """Tests del modelo Role."""
    
    def test_role_creation(self, db: Session, admin_role: Role):
        """Verifica creación de rol con permisos."""
        assert admin_role.name == "admin"
        assert len(admin_role.permissions) == 2
    
    def test_has_permission(self, admin_role: Role):
        """Verifica método has_permission."""
        assert admin_role.has_permission("manage_users") is True
        assert admin_role.has_permission("nonexistent") is False


class TestUserWithRole:
    """Tests de usuario con rol."""
    
    def test_user_role_assignment(self, admin_user: User, admin_role: Role):
        """Verifica asignación de rol a usuario."""
        assert admin_user.role is not None
        assert admin_user.role.name == "admin"
    
    def test_user_has_permission(self, admin_user: User):
        """Verifica que usuario hereda permisos de rol."""
        assert admin_user.has_permission("manage_users") is True
        assert admin_user.has_permission("unknown_permission") is False
    
    def test_user_without_role(self, db: Session):
        """Usuario sin rol no tiene permisos."""
        user = User(
            email="norole@example.com",
            password=get_password_hash("password"),
            name="No",
            lastname="Role"
        )
        db.add(user)
        db.commit()
        
        assert user.role is None
        assert user.has_permission("anything") is False


class TestRolesEndpoint:
    """Tests de endpoints de roles."""
    
    def test_list_roles_requires_admin(self, client: TestClient, auth_headers: dict):
        """Usuario normal no puede listar roles."""
        response = client.get("/api/v1/roles/", headers=auth_headers)
        assert response.status_code == 403
    
    def test_list_roles_as_admin(
        self, client: TestClient, admin_headers: dict, admin_role: Role
    ):
        """Admin puede listar roles."""
        response = client.get("/api/v1/roles/", headers=admin_headers)
        assert response.status_code == 200
        roles = response.json()
        assert len(roles) >= 1
        assert any(r["name"] == "admin" for r in roles)
    
    def test_create_role_as_admin(self, client: TestClient, admin_headers: dict):
        """Admin puede crear roles."""
        response = client.post(
            "/api/v1/roles/",
            headers=admin_headers,
            json={"name": "moderator", "description": "Moderador"}
        )
        assert response.status_code == 201
        assert response.json()["name"] == "moderator"
    
    def test_assign_role_to_user(
        self,
        client: TestClient,
        admin_headers: dict,
        db: Session,
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
        db.commit()
        db.refresh(user)
        
        # Asignar rol
        response = client.post(
            "/api/v1/roles/assign",
            headers=admin_headers,
            json={"user_id": user.id, "role_id": user_role.id}
        )
        assert response.status_code == 200
        
        # Verificar
        db.refresh(user)
        assert user.role_id == user_role.id


class TestRequirePermission:
    """Tests de la dependencia require_permission."""
    
    def test_user_without_permission_denied(
        self, client: TestClient, auth_headers: dict
    ):
        """Usuario sin permiso específico es rechazado."""
        # El endpoint de roles requiere admin
        response = client.get("/api/v1/roles/", headers=auth_headers)
        assert response.status_code == 403
