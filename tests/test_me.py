"""
Tests for current user (me) endpoints (Async).
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
class TestMe:
    """Tests for /api/v1/me endpoints."""

    async def test_get_me(self, client: AsyncClient, auth_headers, test_user):
        """Test getting current user profile."""
        response = await client.get("/api/v1/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert "password" not in data

    async def test_get_me_unauthorized(self, client: AsyncClient):
        """Test getting profile without auth fails."""
        response = await client.get("/api/v1/me")

        assert response.status_code == 401

    async def test_update_me(self, client: AsyncClient, auth_headers):
        """Test updating current user profile."""
        response = await client.put(
            "/api/v1/me",
            headers=auth_headers,
            json={"name": "Updated", "lastname": "Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["lastname"] == "Name"

    async def test_update_me_partial(self, client: AsyncClient, auth_headers, test_user):
        """Test partial update only changes specified fields."""
        response = await client.put(
            "/api/v1/me",
            headers=auth_headers,
            json={"name": "OnlyName"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "OnlyName"
        assert data["lastname"] == test_user.lastname

    async def test_update_me_password(self, client: AsyncClient, auth_headers):
        """Test updating password via PUT /me."""
        response = await client.put(
            "/api/v1/me",
            headers=auth_headers,
            json={"password": "NewStrongPass123!@#"}
        )
        assert response.status_code == 200

        # Login con nueva contraseña
        login_response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "NewStrongPass123!@#"}
        )
        assert login_response.status_code == 200

    async def test_update_me_weak_password_rejected(self, client: AsyncClient, auth_headers):
        """Test that weak password is rejected on update."""
        response = await client.put(
            "/api/v1/me",
            headers=auth_headers,
            json={"password": "weak"}
        )
        assert response.status_code == 422

    async def test_delete_me(self, client: AsyncClient, auth_headers):
        """Test deleting current user account."""
        response = await client.delete("/api/v1/me", headers=auth_headers)
        assert response.status_code == 204

    async def test_delete_me_then_access_fails(self, client: AsyncClient, auth_headers):
        """Test accessing account after deletion fails."""
        await client.delete("/api/v1/me", headers=auth_headers)

        response = await client.get("/api/v1/me", headers=auth_headers)
        assert response.status_code == 401
