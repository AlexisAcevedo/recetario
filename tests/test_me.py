"""
Tests for current user (me) endpoints.
"""
import pytest


class TestMe:
    """Tests for /api/v1/me endpoints."""

    def test_get_me(self, client, auth_headers, test_user):
        """Test getting current user profile."""
        response = client.get("/api/v1/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name

    def test_get_me_unauthorized(self, client):
        """Test getting profile without auth fails."""
        response = client.get("/api/v1/me")
        
        assert response.status_code == 401

    def test_update_me(self, client, auth_headers):
        """Test updating current user profile."""
        response = client.put(
            "/api/v1/me",
            headers=auth_headers,
            json={"name": "Updated", "lastname": "Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["lastname"] == "Name"

    def test_update_me_partial(self, client, auth_headers, test_user):
        """Test partial update only changes specified fields."""
        response = client.put(
            "/api/v1/me",
            headers=auth_headers,
            json={"name": "OnlyName"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "OnlyName"
        assert data["lastname"] == test_user.lastname  # Unchanged

    def test_delete_me(self, client, auth_headers):
        """Test deleting current user account."""
        response = client.delete("/api/v1/me", headers=auth_headers)
        
        assert response.status_code == 204

    def test_delete_me_then_access_fails(self, client, auth_headers):
        """Test accessing account after deletion fails."""
        # Delete account
        client.delete("/api/v1/me", headers=auth_headers)
        
        # Try to access - should fail
        response = client.get("/api/v1/me", headers=auth_headers)
        assert response.status_code == 401
