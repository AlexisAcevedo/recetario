"""
Tests de seguridad: SQL injection, XSS, auth bypass, validación de inputs.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash, create_session_with_tokens


@pytest.mark.asyncio
class TestSQLInjection:
    """Verifica que SQL injection no es posible."""

    async def test_sql_injection_in_user_id(self, client: AsyncClient, auth_headers):
        """SQL injection en path parameter user_id."""
        payloads = [
            "1; DROP TABLE users;--",
            "1' OR '1'='1",
            "1 UNION SELECT * FROM users--",
        ]
        for payload in payloads:
            response = await client.get(
                f"/api/v1/users/{payload}", headers=auth_headers
            )
            assert response.status_code == 422, f"Payload '{payload}' debería ser rechazado"

    async def test_sql_injection_in_login_email(self, client: AsyncClient):
        """SQL injection en campo email de login."""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "' OR 1=1 --",
                "password": "anything"
            }
        )
        assert response.status_code == 401

    async def test_sql_injection_in_create_user(self, client: AsyncClient):
        """SQL injection en campos de creación de usuario."""
        response = await client.post("/api/v1/users", json={
            "email": "test@example.com",
            "password": "StrongPass123!@#",
            "name": "'; DROP TABLE users; --",
            "lastname": "Test"
        })
        # Debe aceptarse como string literal (Pydantic/SQLAlchemy parametrizan)
        if response.status_code == 201:
            data = response.json()
            assert data["name"] == "'; DROP TABLE users; --"


@pytest.mark.asyncio
class TestXSS:
    """Verifica que XSS es almacenado como texto plano, no ejecutado."""

    async def test_xss_in_user_name(self, client: AsyncClient):
        """Scripts en nombre se almacenan como texto plano."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror='alert(1)'>",
        ]
        for i, payload in enumerate(xss_payloads):
            response = await client.post("/api/v1/users", json={
                "email": f"xss{i}@example.com",
                "password": "StrongPass123!@#",
                "name": payload,
                "lastname": "User"
            })
            if response.status_code == 201:
                # Se almacena como texto, no se interpreta
                data = response.json()
                assert data["name"] == payload


@pytest.mark.asyncio
class TestAuthBypass:
    """Verifica que no se puede evadir la autenticación."""

    async def test_refresh_token_as_access_token(self, client: AsyncClient, test_user):
        """Refresh token NO funciona como access token."""
        login_res = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "TestPass123!@#"}
        )
        refresh_token = login_res.json()["refresh_token"]

        response = await client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )
        assert response.status_code == 401

    async def test_cross_user_session_revoke(
        self, client: AsyncClient, auth_headers, db: AsyncSession, test_user
    ):
        """Un usuario NO puede revocar sesiones de otro usuario."""
        user2 = User(
            email="other@example.com",
            password=get_password_hash("OtherPass123!@#"),
            name="Other", lastname="User"
        )
        db.add(user2)
        await db.commit()
        await db.refresh(user2)

        _, _ = await create_session_with_tokens(db, user2.id)

        from sqlalchemy import select
        from app.models.session import Session as SessionModel
        result = await db.execute(
            select(SessionModel).filter(SessionModel.user_id == user2.id)
        )
        session2 = result.scalar_one()

        # test_user intenta revocar sesión de user2
        response = await client.delete(
            f"/api/v1/me/sessions/{session2.id}", headers=auth_headers
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestInputValidation:
    """Tests de validación de inputs edge cases."""

    async def test_invalid_emails(self, client: AsyncClient):
        """Emails inválidos son rechazados."""
        invalid_emails = [
            "invalid",
            "test@",
            "@example.com",
            "",
        ]
        for email in invalid_emails:
            response = await client.post("/api/v1/users", json={
                "email": email,
                "password": "StrongPass123!@#",
                "name": "Test", "lastname": "User"
            })
            assert response.status_code == 422, f"Email '{email}' debería ser rechazado"

    async def test_name_too_short(self, client: AsyncClient):
        """Nombre con 1 carácter es rechazado (min_length=2)."""
        response = await client.post("/api/v1/users", json={
            "email": "short@example.com",
            "password": "StrongPass123!@#",
            "name": "x",
            "lastname": "User"
        })
        assert response.status_code == 422

    async def test_name_too_long(self, client: AsyncClient):
        """Nombre con >100 caracteres es rechazado."""
        response = await client.post("/api/v1/users", json={
            "email": "long@example.com",
            "password": "StrongPass123!@#",
            "name": "x" * 101,
            "lastname": "User"
        })
        assert response.status_code == 422

    async def test_lastname_too_short(self, client: AsyncClient):
        """Apellido con 1 carácter es rechazado."""
        response = await client.post("/api/v1/users", json={
            "email": "short2@example.com",
            "password": "StrongPass123!@#",
            "name": "Test",
            "lastname": "x"
        })
        assert response.status_code == 422

    async def test_password_exactly_12_chars(self, client: AsyncClient):
        """Contraseña con exactamente 12 caracteres es aceptada."""
        response = await client.post("/api/v1/users", json={
            "email": "min12@example.com",
            "password": "Abcdefgh12!@",
            "name": "Test", "lastname": "User"
        })
        assert response.status_code == 201

    async def test_password_11_chars_rejected(self, client: AsyncClient):
        """Contraseña con 11 caracteres es rechazada."""
        response = await client.post("/api/v1/users", json={
            "email": "min11@example.com",
            "password": "Abcdefg12!@",
            "name": "Test", "lastname": "User"
        })
        assert response.status_code == 422

    async def test_empty_password_rejected(self, client: AsyncClient):
        """Contraseña vacía es rechazada."""
        response = await client.post("/api/v1/users", json={
            "email": "empty@example.com",
            "password": "",
            "name": "Test", "lastname": "User"
        })
        assert response.status_code == 422

    async def test_session_id_negative_rejected(self, client: AsyncClient, auth_headers):
        """session_id negativo es rechazado."""
        response = await client.delete(
            "/api/v1/me/sessions/-1", headers=auth_headers
        )
        assert response.status_code == 422

    async def test_user_id_negative_rejected(self, client: AsyncClient, auth_headers):
        """user_id negativo en path es rechazado."""
        response = await client.get(
            "/api/v1/users/-1", headers=auth_headers
        )
        assert response.status_code == 422

    async def test_pagination_per_page_zero(self, client: AsyncClient, auth_headers):
        """per_page=0 es rechazado."""
        response = await client.get(
            "/api/v1/users?per_page=0", headers=auth_headers
        )
        assert response.status_code == 422

    async def test_pagination_high_page_returns_empty(self, client: AsyncClient, auth_headers):
        """Página muy alta retorna items vacíos."""
        response = await client.get(
            "/api/v1/users?page=999999", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["items"] == []


@pytest.mark.asyncio
class TestSecurityHeaders:
    """Verifica que los headers de seguridad están presentes."""

    async def test_security_headers_present(self, client: AsyncClient):
        """Verifica headers de seguridad en respuestas."""
        response = await client.get("/")
        headers = response.headers

        assert headers.get("x-content-type-options") == "nosniff"
        assert headers.get("x-frame-options") == "DENY"
        assert "strict-transport-security" in headers
        assert "content-security-policy" in headers
        assert "referrer-policy" in headers
        assert "permissions-policy" in headers
        assert "x-permitted-cross-domain-policies" in headers


@pytest.mark.asyncio
class TestMetricsEndpoint:
    """Verifica el endpoint de métricas."""

    async def test_metrics_returns_prometheus_format(self, client: AsyncClient):
        """GET /metrics retorna métricas de Prometheus."""
        response = await client.get("/metrics")
        assert response.status_code == 200
