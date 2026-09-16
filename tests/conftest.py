import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from database import engine, Base, AsyncSessionLocal
from main import app
import auth
import models
import crud
import schemas

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def create_authenticated_headers():
    async def _headers(tenant_id: str, email: str = "test@example.com", password: str = "password123"):
        async with AsyncSessionLocal() as db:
            user = await crud.get_user_by_email(db, email=email, tenant_id=tenant_id)
            if not user:
                hashed_pw = auth.get_password_hash(password)
                user = models.User(
                    email=email,
                    hashed_password=hashed_pw,
                    tenant_id=tenant_id
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

        token = auth.create_access_token(data={"sub": email, "tenant_id": tenant_id})
        return {
            "X-Tenant-ID": tenant_id,
            "Authorization": f"Bearer {token}"
        }
    return _headers
