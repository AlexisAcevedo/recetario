"""
Tests para gestión de sesiones y refresh tokens.
"""
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.session import Session as SessionModel
from app.core.security import create_session_with_tokens, get_password_hash
from app.models.user import User


class TestSessionModel:
    """Tests del modelo Session."""
    
    def test_session_creation(self, db: Session, test_user: User):
        """Verifica creación de modelo Session."""
        access, refresh = create_session_with_tokens(
            db, test_user.id, "TestDevice", "127.0.0.1"
        )
        
        session = db.query(SessionModel).filter(SessionModel.user_id == test_user.id).first()
        assert session is not None
        assert session.refresh_token == refresh
        assert session.device_info == "TestDevice"
        assert session.ip_address == "127.0.0.1"
        assert session.is_valid() is True

    def test_session_revoked(self, db: Session, test_user: User):
        """Verifica validación de sesión revocada."""
        _, refresh = create_session_with_tokens(db, test_user.id)
        session = db.query(SessionModel).filter(SessionModel.refresh_token == refresh).first()
        
        session.is_revoked = True
        db.commit()
        
        assert session.is_valid() is False


class TestRefreshEndpoint:
    """Tests endpoint /auth/refresh."""
    
    def test_refresh_token_success(self, client: TestClient, db: Session, test_user: User):
        """Renovación exitosa de access token."""
        # Crear sesión manual
        _, refresh = create_session_with_tokens(db, test_user.id)
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """Fallo con token inválido."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token_123"}
        )
        assert response.status_code == 401


class TestSessionManagement:
    """Tests gestión de sesiones en /me/sessions."""
    
    def test_list_sessions(self, client: TestClient, auth_headers: dict, db: Session, test_user: User):
        """Listar sesiones activas."""
        # Crear una sesión extra direct en DB
        create_session_with_tokens(db, test_user.id, "Device2")
        
        response = client.get("/api/v1/me/sessions", headers=auth_headers)
        assert response.status_code == 200
        sessions = response.json()
        assert len(sessions) >= 1  # Al menos la del login actual o la creada
    
    def test_revoke_session(self, client: TestClient, auth_headers: dict, db: Session, test_user: User):
        """Revocar una sesión específica."""
        # Crear sesión a revocar
        _, refresh = create_session_with_tokens(db, test_user.id)
        session = db.query(SessionModel).filter(SessionModel.refresh_token == refresh).first()
        
        response = client.delete(f"/api/v1/me/sessions/{session.id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verificar en DB
        db.refresh(session)
        assert session.is_revoked is True
