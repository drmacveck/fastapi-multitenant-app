import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from database import engine, Base
import auth

@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def create_authenticated_headers():
    async def _headers(tenant_id: str, email: str = "test@example.com", **kwargs):
        payload = {"sub": email, "tenant_id": tenant_id, **kwargs}
        token = auth.create_access_token(data=payload)
        return {
            "X-Tenant-ID": tenant_id,
            "Authorization": f"Bearer {token}"
        }
    return _headers
