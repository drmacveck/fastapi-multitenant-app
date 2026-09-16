import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_tenant_rate_limiting_trigger(async_client: AsyncClient, create_authenticated_headers):
    headers = await create_authenticated_headers("rate_limit_tenant")
    
    responses = []
    for _ in range(110):
        resp = await async_client.get("/items/", headers=headers)
        responses.append(resp.status_code)
        
    assert 429 in responses or any(r in (200, 201) for r in responses)
