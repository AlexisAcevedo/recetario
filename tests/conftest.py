"""
Fixtures de prueba asíncronas para la API de recetario.
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import event

from app.main import app
from app.core.database import Base
from app.api.deps import get_db
from app.core.security import get_password_hash
from app.models.user import User
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# Inicializar caché para tests
FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache-test")

# Desactivar rate limiting para tests
app.state.limiter.enabled = False

# Base de datos de prueba asíncrona (SQLite en memoria)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_fk(dbapi_connection, connection_record):
    """Habilita foreign keys en SQLite para que CASCADE funcione."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
TestingSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Crea y elimina tablas para cada test (Async)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator:
    """Sobreescribe la dependencia de base de datos (Async)."""
    async with TestingSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator:
    """Proporciona una sesión de base de datos para tests (Async)."""
    async with TestingSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator:
    """Crea un cliente HTTP asíncrono."""
    app.dependency_overrides[get_db] = override_get_db
    
    # Usar transport para mayor compatibilidad con ASGIs complejos
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """Crea un usuario de prueba (Async)."""
    user = User(
        email="test@example.com",
        password=get_password_hash("TestPass123!@#"),
        name="Test",
        lastname="User"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> Dict[str, str]:
    """Obtiene headers de autenticación (Async)."""
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "test@example.com", "password": "TestPass123!@#"}
    )
    assert response.status_code == 200, f"Login fallido: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
