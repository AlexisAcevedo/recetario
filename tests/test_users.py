"""
Tests de Usuarios asíncronos.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUsers:
    """Suite de pruebas para CRUD de usuarios (Async)."""

    async def test_create_user(self, client: AsyncClient):
        """Prueba la creación de un nuevo usuario."""
        user_data = {
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "name": "New",
            "lastname": "User"
        }
        response = await client.post("/api/v1/users", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data

    async def test_create_user_duplicate_email(self, client: AsyncClient, test_user):
        """Prueba que no se permita duplicar emails."""
        user_data = {
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "name": "Duplicate",
            "lastname": "User"
        }
        response = await client.post("/api/v1/users", json=user_data)

        assert response.status_code == 400
        assert "registrado" in response.json()["detail"].lower()

    async def test_list_users_authenticated(self, client: AsyncClient, auth_headers):
        """Prueba listar usuarios con autenticación."""
        response = await client.get("/api/v1/users", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    async def test_list_users_unauthenticated(self, client: AsyncClient):
        """Prueba que listar usuarios sin auth falla."""
        response = await client.get("/api/v1/users")
        assert response.status_code == 401

    async def test_get_user_by_id(self, client: AsyncClient, auth_headers, test_user):
        """Prueba obtener un usuario por ID."""
        response = await client.get(
            f"/api/v1/users/{test_user.id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["email"] == test_user.email

    async def test_get_user_by_id_unauthenticated(self, client: AsyncClient, test_user):
        """Prueba que obtener usuario sin auth falla."""
        response = await client.get(f"/api/v1/users/{test_user.id}")
        assert response.status_code == 401

    async def test_get_user_not_found(self, client: AsyncClient, auth_headers):
        """Prueba obtener usuario inexistente."""
        response = await client.get("/api/v1/users/99999", headers=auth_headers)
        assert response.status_code == 404

    async def test_create_user_weak_password_no_uppercase(self, client: AsyncClient):
        """Prueba que se rechace contraseña sin mayúsculas."""
        response = await client.post("/api/v1/users", json={
            "email": "weak1@example.com",
            "password": "nouppercase123!",
            "name": "Test", "lastname": "User"
        })
        assert response.status_code == 422

    async def test_create_user_weak_password_no_special(self, client: AsyncClient):
        """Prueba que se rechace contraseña sin símbolos."""
        response = await client.post("/api/v1/users", json={
            "email": "weak2@example.com",
            "password": "NoSpecialChar123",
            "name": "Test", "lastname": "User"
        })
        assert response.status_code == 422

    async def test_create_user_common_password(self, client: AsyncClient):
        """Prueba que se rechace contraseña común."""
        response = await client.post("/api/v1/users", json={
            "email": "weak3@example.com",
            "password": "Password123!@#",
            "name": "Test", "lastname": "User"
        })
        assert response.status_code == 422

    async def test_create_user_common_password_variant(self, client: AsyncClient):
        """Prueba que se rechace otra contraseña común."""
        response = await client.post("/api/v1/users", json={
            "email": "weak4@example.com",
            "password": "Changeme1234!",
            "name": "Test", "lastname": "User"
        })
        assert response.status_code == 422

    async def test_create_user_unicode_name(self, client: AsyncClient):
        """Prueba creación con caracteres Unicode en nombre."""
        response = await client.post("/api/v1/users", json={
            "email": "unicode@example.com",
            "password": "StrongPass123!@#",
            "name": "José María",
            "lastname": "García López"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "José María"

    async def test_pagination_invalid_page_zero(self, client: AsyncClient, auth_headers):
        """Prueba que page=0 es rechazado."""
        response = await client.get(
            "/api/v1/users?page=0", headers=auth_headers
        )
        assert response.status_code == 422

    async def test_pagination_invalid_negative_page(self, client: AsyncClient, auth_headers):
        """Prueba que page negativo es rechazado."""
        response = await client.get(
            "/api/v1/users?page=-1", headers=auth_headers
        )
        assert response.status_code == 422

    async def test_pagination_per_page_limit(self, client: AsyncClient, auth_headers):
        """Prueba que per_page > 1000 es rechazado."""
        response = await client.get(
            "/api/v1/users?per_page=5000", headers=auth_headers
        )
        assert response.status_code == 422
