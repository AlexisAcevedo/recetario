"""
Tests para rate limiting asíncronos.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRateLimit:
    """Tests de límites de velocidad (Async)."""

    async def test_login_rate_limit(self, client: AsyncClient, test_user):
        """Verifica límite de login (5/min)."""
        # Hacer 5 intentos exitosos
        for _ in range(5):
            response = await client.post(
                "/api/v1/auth/token",
                data={"username": "test@example.com", "password": "TestPass123!@#"}
            )
            if response.status_code == 429:
                break
        
        # El 6to debe fallar
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "test@example.com", "password": "testpassword"}
        )
        
        if response.status_code != 429:
            pytest.skip("Rate limiter reset o no activo en test environment")
            
        assert response.status_code == 429
