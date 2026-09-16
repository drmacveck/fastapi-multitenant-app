import json
import os

import pytest
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

@pytest.mark.asyncio
async def test_items_caching_and_invalidation():
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        tenant_id = "tenant_test"
        cache_key = f"tenant:{tenant_id}:item_1"
        data = {"id": 1, "name": "Test Item"}

        # Set cache
        await client.set(cache_key, json.dumps(data), ex=60)

        # Get cache
        cached_val = await client.get(cache_key)
        assert json.loads(cached_val) == data

        # Invalidate cache
        keys = await client.keys(f"tenant:{tenant_id}:*")
        if keys:
            await client.delete(*keys)

        # Verify invalidation
        purged_val = await client.get(cache_key)
        assert purged_val is None
    finally:
        await client.aclose()
