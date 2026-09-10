import pytest
import time
from httpx import AsyncClient, ASGITransport

try:
    from main import app
except ImportError:
    from Main import app

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest.mark.anyio
async def test_01_health_and_readiness(client):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    response = await client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"

@pytest.mark.anyio
async def test_02_tenant_isolation_and_flow(client):
    tenant_a = "tenant_alpha"
    tenant_b = "tenant_beta"
    email = f"user_{int(time.time() * 1000)}@example.com"

    # 1. Register under Tenant Alpha
    headers_a = {"X-Tenant-ID": tenant_a}
    response = await client.post("/register", json={"email": email, "password": "pass"}, headers=headers_a)
    assert response.status_code == 201, f"Register failed: {response.text}"
    assert response.json()["tenant_id"] == tenant_a

    # 2. Login under Tenant Alpha
    headers_login_a = {"Content-Type": "application/x-www-form-urlencoded", "X-Tenant-ID": tenant_a}
    response = await client.post("/login", data={"username": email, "password": "pass"}, headers=headers_login_a)
    assert response.status_code == 200, f"Login failed: {response.text}"
    token_a = response.json()["access_token"]

    # 3. Fail Login if wrong tenant header is supplied
    headers_login_b = {"Content-Type": "application/x-www-form-urlencoded", "X-Tenant-ID": tenant_b}
    response = await client.post("/login", data={"username": email, "password": "pass"}, headers=headers_login_b)
    assert response.status_code == 401

    # 4. Create item under Tenant Alpha
    auth_headers_a = {"Authorization": f"Bearer {token_a}", "X-Tenant-ID": tenant_a}
    response = await client.post("/items", json={"text": "Tenant Alpha Resource"}, headers=auth_headers_a)
    assert response.status_code == 201
    assert response.json()["tenant_id"] == tenant_a

    # 5. Access item with Tenant Beta header should fail validation
    auth_headers_b = {"Authorization": f"Bearer {token_a}", "X-Tenant-ID": tenant_b}
    response = await client.get("/items", headers=auth_headers_b)
    assert response.status_code == 401

@pytest.mark.anyio
async def test_03_strict_tenant_data_isolation(client):
    tenant_a = "alpha_corp"
    tenant_b = "beta_inc"
    email_a = f"admin_{int(time.time() * 1000)}@alpha.com"
    email_b = f"admin_{int(time.time() * 1000)}@beta.com"

    # Register & Login Tenant A
    await client.post("/register", json={"email": email_a, "password": "pass"}, headers={"X-Tenant-ID": tenant_a})
    res_a = await client.post("/login", data={"username": email_a, "password": "pass"}, headers={"Content-Type": "application/x-www-form-urlencoded", "X-Tenant-ID": tenant_a})
    token_a = res_a.json()["access_token"]

    # Register & Login Tenant B
    await client.post("/register", json={"email": email_b, "password": "pass"}, headers={"X-Tenant-ID": tenant_b})
    res_b = await client.post("/login", data={"username": email_b, "password": "pass"}, headers={"Content-Type": "application/x-www-form-urlencoded", "X-Tenant-ID": tenant_b})
    token_b = res_b.json()["access_token"]

    # Tenant A creates an item
    auth_a = {"Authorization": f"Bearer {token_a}", "X-Tenant-ID": tenant_a}
    item_res = await client.post("/items", json={"text": "Confidential Alpha Data"}, headers=auth_a)
    assert item_res.status_code == 201

    # Tenant B queries items - must not see Tenant A's items
    auth_b = {"Authorization": f"Bearer {token_b}", "X-Tenant-ID": tenant_b}
    list_res = await client.get("/items", headers=auth_b)
    assert list_res.status_code == 200
    data = list_res.json()
    items = data.get("items", data if isinstance(data, list) else [])
    assert all(item["tenant_id"] == tenant_b for item in items)

@pytest.mark.anyio
async def test_04_missing_tenant_header_rejection(client):
    response = await client.post("/register", json={"email": "no_tenant@example.com", "password": "pass"})
    assert response.status_code in (400, 422)
