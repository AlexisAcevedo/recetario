"""
Tests for current user (me) endpoints (Async).
"""
import pytest
from httpx import AsyncClient


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
        assert data["lastname"] == test_user.lastname  # Unchanged

    @pytest.mark.skip(reason="Requiere ON DELETE CASCADE en sessions - pendiente migración")
    async def test_delete_me(self, client: AsyncClient, auth_headers):
        """Test deleting current user account."""
        response = await client.delete("/api/v1/me", headers=auth_headers)
        
        assert response.status_code == 204

    @pytest.mark.skip(reason="Requiere ON DELETE CASCADE en sessions - pendiente migración")
    async def test_delete_me_then_access_fails(self, client: AsyncClient, auth_headers):
        """Test accessing account after deletion fails."""
        # Delete account
        await client.delete("/api/v1/me", headers=auth_headers)
        
        # Try to access - should fail
        response = await client.get("/api/v1/me", headers=auth_headers)
        assert response.status_code == 401
