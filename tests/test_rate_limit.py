"""
Tests para rate limiting asíncronos.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.deps import get_db
from tests.conftest import override_get_db


@pytest_asyncio.fixture
async def client_with_rate_limit() -> AsyncClient:
    """Cliente con rate limiter activado."""
    app.dependency_overrides[get_db] = override_get_db
    app.state.limiter.enabled = True
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.state.limiter.enabled = False
    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestRateLimit:
    """Tests de límites de velocidad (Async)."""

    async def test_login_rate_limit(self, client_with_rate_limit: AsyncClient, test_user):
        """Verifica límite de login (5/min)."""
        client = client_with_rate_limit
        last_status = None

        for i in range(7):
            response = await client.post(
                "/api/v1/auth/token",
                data={"username": "test@example.com", "password": "TestPass123!@#"}
            )
            last_status = response.status_code
            if last_status == 429:
                break

        assert last_status == 429, "Rate limiter debería bloquear después de 5 intentos"
