"""
Tests for user endpoints.
"""
import pytest


class TestUsers:
    """Tests for /api/v1/users endpoints."""

    def test_create_user(self, client):
        """Test creating a new user."""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "new@example.com",
                "password": "NewPass123!@#",
                "name": "New",
                "lastname": "User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["name"] == "New"
        assert "password" not in data  # Password should not be returned

    def test_create_user_duplicate_email(self, client, test_user):
        """Test creating user with existing email fails."""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "password": "AnyPass123!@#",
                "name": "Another",
                "lastname": "User"
            }
        )
        
        assert response.status_code == 400

    def test_create_user_invalid_email(self, client):
        """Test creating user with invalid email fails."""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "not-an-email",
                "password": "ValidPass123!@#",
                "name": "Test",
                "lastname": "User"
            }
        )
        
        assert response.status_code == 422

    def test_create_user_short_password(self, client):
        """Test creating user with short password fails."""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "valid@example.com",
                "password": "short",  # Less than 8 chars
                "name": "Test",
                "lastname": "User"
            }
        )
        
        assert response.status_code == 422

    def test_get_user_by_id(self, client, test_user):
        """Test getting user by ID."""
        response = client.get(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email

    def test_get_user_not_found(self, client):
        """Test getting non-existent user fails."""
        response = client.get("/api/v1/users/9999")
        
        assert response.status_code == 404

    def test_list_users_requires_auth(self, client):
        """Test listing users requires authentication."""
        response = client.get("/api/v1/users")
        
        assert response.status_code == 401

    def test_list_users_authenticated(self, client, auth_headers):
        """Test listing users when authenticated."""
        response = client.get("/api/v1/users", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Response ahora es paginada
        assert "items" in data or isinstance(data, list)
