"""
Tests End-to-End para flujos completos de la API.
Verifica flujos de autenticación, rate limiting y validación de contraseñas.
"""
import pytest


class TestAuthenticationFlow:
    """Flujo de autenticación basico."""

    def test_login_success(self, client, test_user):
        """Test login exitoso con credenciales válidas."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPass123!@#"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user):
        """Test login fallido con credenciales inválidas."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self, client):
        """Test acceso a endpoint protegido sin token."""
        response = client.get("/api/v1/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_token(self, client, auth_headers):
        """Test acceso a endpoint protegido con token válido."""
        response = client.get("/api/v1/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"


class TestRefreshTokenFlow:
    """Flujo de refresh token."""

    def test_refresh_token_flow(self, client, test_user):
        """Test del flujo de renovación de tokens."""
        # 1. LOGIN INICIAL
        login_response = client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPass123!@#"}
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        refresh_token = tokens["refresh_token"]
        
        # 2. USAR REFRESH TOKEN
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens

    def test_invalid_refresh_token_rejected(self, client):
        """Test que un refresh token inválido es rechazado."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token-here"}
        )
        assert response.status_code in [401, 403, 400]


class TestPasswordValidation:
    """Verificación de validación de contraseñas."""

    def test_weak_password_rejected(self, client):
        """Test que contraseñas débiles son rechazadas."""
        weak_passwords = [
            "short1!",           # Muy corta
            "alllowercase123!",  # Sin mayúsculas
            "ALLUPPERCASE123!",  # Sin minúsculas  
            "NoNumbers!!!",      # Sin números
            "NoSymbols12345",    # Sin símbolos
        ]
        
        for idx, password in enumerate(weak_passwords):
            response = client.post(
                "/api/v1/users",
                json={
                    "email": f"weak{idx}@test.com",
                    "password": password,
                    "name": "Test",
                    "lastname": "User"
                }
            )
            assert response.status_code == 422, f"Password '{password}' debería ser rechazada"

    def test_strong_password_accepted(self, client):
        """Test que contraseñas fuertes son aceptadas."""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "secure@example.com",
                "password": "MyV3ryStr0ng!Pass#2024",
                "name": "Secure",
                "lastname": "User"
            }
        )
        assert response.status_code == 201


class TestPaginatedResponse:
    """Verificación de respuestas paginadas."""

    def test_users_pagination_structure(self, client, auth_headers):
        """Test que GET /users retorna estructura paginada."""
        response = client.get("/api/v1/users?page=1&per_page=10", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
        
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)


class TestHealthEndpoints:
    """Verificación de endpoints de salud."""

    def test_root_endpoint(self, client):
        """Test endpoint raíz."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_endpoint(self, client):
        """Test endpoint de health."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
