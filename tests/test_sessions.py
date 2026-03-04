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
        # Crear sesión manual
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


@pytest.mark.asyncio
class TestSessionManagement:
    """Tests gestión de sesiones en /me/sessions (Async)."""
    
    async def test_list_sessions(self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User):
        """Listar sesiones activas (Async)."""
        # Crear una sesión extra directa en DB
        await create_session_with_tokens(db, test_user.id, "Device2")
        
        response = await client.get("/api/v1/me/sessions", headers=auth_headers)
        assert response.status_code == 200
        sessions = response.json()
        assert len(sessions) >= 1
    
    async def test_revoke_session(self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User):
        """Revocar una sesión específica (Async)."""
        # Crear sesión a revocar
        _, refresh = await create_session_with_tokens(db, test_user.id)
        
        result = await db.execute(select(SessionModel).filter(SessionModel.refresh_token == refresh))
        session = result.scalar_one_or_none()
        
        response = await client.delete(f"/api/v1/me/sessions/{session.id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verificar en DB
        await db.refresh(session)
        assert session.is_revoked is True
