import pytest
from httpx import AsyncClient, ASGITransport
from config import settings

try:
    from main import app
except ImportError:
    from Main import app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
