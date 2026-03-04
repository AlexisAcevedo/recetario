"""
Tests de Autenticación asíncronos.
"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestAuth:
    """Suite de pruebas para login (Async)."""

    async def test_login_success(self, client: AsyncClient, test_user):
        """Prueba login exitoso con credenciales válidas."""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPass123!@#"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Prueba login con contraseña incorrecta."""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "WrongPassword123"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Email o contraseña incorrectos"

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Prueba login con usuario no registrado."""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "nonexistent@example.com", "password": "SomePassword123"}
        )
        
        assert response.status_code == 401
