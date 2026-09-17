import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

os.environ["POSTGRES_HOST"] = os.getenv("POSTGRES_HOST", "localhost")
os.environ["REDIS_HOST"] = os.getenv("REDIS_HOST", "localhost")

from app.main import app  # isort: skip


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture(scope="function")
def create_authenticated_headers():
    async def _headers(tenant_id: str, email: str = "test@example.com"):
        return {
            "X-Tenant-ID": tenant_id,
            "Authorization": f"Bearer mock-token-{tenant_id}",
        }

    return _headers
