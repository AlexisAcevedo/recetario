"""
Tests de Autenticación asíncronos.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_session_with_tokens


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

    async def test_access_with_expired_token(self, client: AsyncClient, test_user):
        """Prueba acceso con token expirado."""
        from datetime import timedelta
        expired_token = create_access_token(
            data={"user_id": test_user.id},
            expires_delta=timedelta(seconds=-1)
        )
        response = await client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

    async def test_access_with_invalid_token(self, client: AsyncClient):
        """Prueba acceso con token manipulado."""
        response = await client.get(
            "/api/v1/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    async def test_access_with_empty_bearer(self, client: AsyncClient):
        """Prueba acceso con Bearer vacío."""
        response = await client.get(
            "/api/v1/me",
            headers={"Authorization": "Bearer "}
        )
        assert response.status_code == 401

    async def test_logout(self, client: AsyncClient, auth_headers, db: AsyncSession, test_user):
        """Prueba que logout revoca sesiones."""
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 204

    async def test_refresh_after_logout_fails(self, client: AsyncClient, test_user, db: AsyncSession):
        """Prueba que refresh falla después de logout."""
        # Login
        login_res = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPass123!@#"}
        )
        tokens = login_res.json()

        # Logout
        await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        # Refresh debería fallar
        refresh_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh_res.status_code == 401
