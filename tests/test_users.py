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
