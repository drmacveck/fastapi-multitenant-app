import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_01_health_and_readiness(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_02_tenant_isolation_and_flow(async_client: AsyncClient, create_authenticated_headers):
    headers = await create_authenticated_headers("tenant_a")
    create_res = await async_client.post("/items/", json={"name": "Widget A"}, headers=headers)
    assert create_res.status_code in (200, 201)
    
    get_res = await async_client.get("/items/", headers=headers)
    assert get_res.status_code == 200
    items = get_res.json()
    assert len(items) >= 1

@pytest.mark.asyncio
async def test_03_strict_tenant_data_isolation(async_client: AsyncClient, create_authenticated_headers):
    headers_a = await create_authenticated_headers("tenant_a", email="user_a@example.com")
    headers_b = await create_authenticated_headers("tenant_b", email="user_b@example.com")

    await async_client.post("/items/", json={"name": "Tenant A Secret"}, headers=headers_a)
    
    res_b = await async_client.get("/items/", headers=headers_b)
    assert res_b.status_code == 200
    items_b = res_b.json()
    assert all(item.get("name") != "Tenant A Secret" for item in items_b)

@pytest.mark.asyncio
async def test_04_missing_tenant_header_rejection(async_client: AsyncClient):
    response = await async_client.get("/items/")
    assert response.status_code in (400, 401, 422)
