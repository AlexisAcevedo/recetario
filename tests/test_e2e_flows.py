"""
Tests E2E (End-to-End) asíncronos para Recetario API.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthenticationFlow:
    """Flujo completo de autenticación (Async)."""

    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPass123!@#"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_login_invalid_credentials(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "wrong@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        response = await client.get("/api/v1/users")
        assert response.status_code == 401

    async def test_protected_endpoint_with_token(self, client: AsyncClient, auth_headers):
        response = await client.get("/api/v1/users", headers=auth_headers)
        assert response.status_code == 200


@pytest.mark.asyncio
class TestRefreshTokenFlow:
    """Flujo de renovación de tokens (Async)."""

    async def test_refresh_token_flow(self, client: AsyncClient, test_user):
        # 1. Login inicial
        login_res = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPass123!@#"}
        )
        refresh_token = login_res.json()["refresh_token"]

        # 2. Refresh
        refresh_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_res.status_code == 200
        assert "access_token" in refresh_res.json()

    async def test_invalid_refresh_token_rejected(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token-123"}
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestFullUserLifecycle:
    """Flujo completo: registro -> login -> uso -> logout."""

    async def test_register_login_use_logout(self, client: AsyncClient):
        # 1. Registro
        reg_res = await client.post("/api/v1/users", json={
            "email": "lifecycle@example.com",
            "password": "LifeCycle123!@#",
            "name": "Life", "lastname": "Cycle"
        })
        assert reg_res.status_code == 201

        # 2. Login
        login_res = await client.post(
            "/api/v1/auth/token",
            data={"username": "lifecycle@example.com", "password": "LifeCycle123!@#"}
        )
        assert login_res.status_code == 200
        tokens = login_res.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # 3. Usar API
        me_res = await client.get("/api/v1/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "lifecycle@example.com"

        # 4. Logout
        logout_res = await client.post("/api/v1/auth/logout", headers=headers)
        assert logout_res.status_code == 204

        # 5. Refresh falla después de logout
        refresh_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh_res.status_code == 401


@pytest.mark.asyncio
class TestPasswordValidation:
    """Validación de complejidad de contraseñas (Async)."""

    async def test_weak_password_rejected(self, client: AsyncClient):
        user_data = {
            "email": "weak@example.com",
            "password": "123",
            "name": "Weak",
            "lastname": "Pass"
        }
        response = await client.post("/api/v1/users", json=user_data)
        assert response.status_code == 422

    async def test_strong_password_accepted(self, client: AsyncClient):
        user_data = {
            "email": "strong@example.com",
            "password": "StrongPass123!@#",
            "name": "Strong",
            "lastname": "Pass"
        }
        response = await client.post("/api/v1/users", json=user_data)
        assert response.status_code == 201


@pytest.mark.asyncio
class TestPaginatedResponse:
    """Estructura de respuestas paginadas (Async)."""

    async def test_users_pagination_structure(self, client: AsyncClient, auth_headers):
        response = await client.get("/api/v1/users?page=1&per_page=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "total_pages" in data


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Endpoints de monitoreo (Async)."""

    async def test_root_endpoint(self, client: AsyncClient):
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    async def test_health_endpoint(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
