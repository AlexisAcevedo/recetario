"""
Tests para gestión de sesiones y refresh tokens (Async).
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.session import Session as SessionModel
from app.core.security import create_session_with_tokens
from app.models.user import User


@pytest.mark.asyncio
class TestSessionModel:
    """Tests del modelo Session."""

    async def test_session_creation(self, db: AsyncSession, test_user: User):
        """Verifica creación de modelo Session (Async)."""
        access, refresh = await create_session_with_tokens(
            db, test_user.id, "TestDevice", "127.0.0.1"
        )

        result = await db.execute(select(SessionModel).filter(SessionModel.user_id == test_user.id))
        session = result.scalar_one_or_none()

        assert session is not None
        assert session.refresh_token == refresh
        assert session.device_info == "TestDevice"
        assert session.ip_address == "127.0.0.1"
        assert session.is_valid() is True

    async def test_session_revoked(self, db: AsyncSession, test_user: User):
        """Verifica validación de sesión revocada (Async)."""
        _, refresh = await create_session_with_tokens(db, test_user.id)

        result = await db.execute(select(SessionModel).filter(SessionModel.refresh_token == refresh))
        session = result.scalar_one_or_none()

        session.is_revoked = True
        await db.commit()

        assert session.is_valid() is False


@pytest.mark.asyncio
class TestRefreshEndpoint:
    """Tests endpoint /auth/refresh (Async)."""

    async def test_refresh_token_success(self, client: AsyncClient, db: AsyncSession, test_user: User):
        """Renovación exitosa de access token (Async)."""
        _, refresh = await create_session_with_tokens(db, test_user.id)

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Fallo con token inválido (Async)."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token_123"}
        )
        assert response.status_code == 401

    async def test_refresh_revoked_token_fails(self, client: AsyncClient, db: AsyncSession, test_user: User):
        """Fallo con refresh token revocado."""
        _, refresh = await create_session_with_tokens(db, test_user.id)

        # Revocar la sesión
        result = await db.execute(select(SessionModel).filter(SessionModel.refresh_token == refresh))
        session = result.scalar_one_or_none()
        session.is_revoked = True
        await db.commit()

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh}
        )
        assert response.status_code == 401

    async def test_double_refresh_same_token(self, client: AsyncClient, db: AsyncSession, test_user: User):
        """Doble refresh con el mismo token funciona (token no cambia)."""
        _, refresh = await create_session_with_tokens(db, test_user.id)

        res1 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
        assert res1.status_code == 200

        res2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
        assert res2.status_code == 200


@pytest.mark.asyncio
class TestSessionManagement:
    """Tests gestión de sesiones en /me/sessions (Async)."""

    async def test_list_sessions(self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User):
        """Listar sesiones activas (Async)."""
        await create_session_with_tokens(db, test_user.id, "Device2")

        response = await client.get("/api/v1/me/sessions", headers=auth_headers)
        assert response.status_code == 200
        sessions = response.json()
        assert len(sessions) >= 1

    async def test_revoke_session(self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User):
        """Revocar una sesión específica (Async)."""
        _, refresh = await create_session_with_tokens(db, test_user.id)

        result = await db.execute(select(SessionModel).filter(SessionModel.refresh_token == refresh))
        session = result.scalar_one_or_none()

        response = await client.delete(f"/api/v1/me/sessions/{session.id}", headers=auth_headers)
        assert response.status_code == 204

        await db.refresh(session)
        assert session.is_revoked is True

    async def test_revoke_session_invalid_id(self, client: AsyncClient, auth_headers: dict):
        """Revocar sesión con ID inválido retorna 404."""
        response = await client.delete("/api/v1/me/sessions/99999", headers=auth_headers)
        assert response.status_code == 404

    async def test_revoke_session_zero_id_rejected(self, client: AsyncClient, auth_headers: dict):
        """Revocar sesión con ID 0 es rechazado por validación."""
        response = await client.delete("/api/v1/me/sessions/0", headers=auth_headers)
        assert response.status_code == 422

    async def test_revoke_all_sessions(self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User):
        """Revocar todas las sesiones (Async)."""
        await create_session_with_tokens(db, test_user.id, "Device2")
        await create_session_with_tokens(db, test_user.id, "Device3")

        response = await client.delete("/api/v1/me/sessions", headers=auth_headers)
        assert response.status_code == 204
