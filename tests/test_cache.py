import json
import os

import pytest
import redis.asyncio as redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"


@pytest.mark.asyncio
async def test_items_caching_and_invalidation():
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        tenant_id = "tenant_test"
        cache_key = f"tenant:{tenant_id}:item_1"
        data = {"id": 1, "name": "Test Item"}

        await client.set(cache_key, json.dumps(data), ex=60)
        cached_val = await client.get(cache_key)
        assert cached_val is not None
        assert json.loads(cached_val) == data

        await client.delete(cache_key)
        assert await client.get(cache_key) is None
    finally:
        await client.aclose()
