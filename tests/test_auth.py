"""
Tests for authentication endpoints.
"""
import pytest


class TestAuth:
    """Tests for /api/v1/auth endpoints."""

    def test_login_success(self, client, test_user):
        """Test successful login returns token."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPass123!@#"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "noone@example.com", "password": "anypassword"}
        )
        
        assert response.status_code == 401
