"""
Fixtures de prueba para la API de recetario.
Configura base de datos en memoria y helpers de autenticación.
"""
import pytest
from typing import Generator, Dict

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base
from app.api.deps import get_db
from app.core.security import get_password_hash
from app.models.user import User

# Base de datos de prueba (SQLite en memoria)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Crea y elimina tablas para cada test."""
    # Reset rate limiter para evitar acumulación entre tests
    from app.core.limiter import limiter
    try:
        limiter.reset()
    except Exception:
        pass  # Limiter puede no tener estado en tests
    
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    """Sobreescribe la dependencia de base de datos para tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator:
    """Proporciona una sesión de base de datos para tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client() -> Generator:
    """Crea un cliente de prueba con base de datos sobreescrita."""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db) -> User:
    """Crea un usuario de prueba en la base de datos."""
    user = User(
        email="test@example.com",
        password=get_password_hash("TestPass123!@#"),  # Contraseña fuerte
        name="Test",
        lastname="User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user) -> Dict[str, str]:
    """Obtiene headers de autenticación para el usuario de prueba."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "test@example.com", "password": "TestPass123!@#"}
    )
    assert response.status_code == 200, f"Login fallido: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
