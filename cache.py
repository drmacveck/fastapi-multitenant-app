import json
import time
from typing import Any

from fastapi import HTTPException, status

from redis_client import redis_client

DEFAULT_TTL = 3600

async def set_cached_json(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    serialized = json.dumps(value)
    await redis_client.set(key, serialized, ex=ttl)

async def get_cached_json(key: str) -> Any | None:
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

async def invalidate_tenant_cache(tenant_id: str | None = None, pattern: str | None = None) -> None:
    target_pattern = pattern if pattern else f"tenant:{tenant_id}:*"
    keys = await redis_client.keys(target_pattern)
    if keys:
        await redis_client.delete(*keys)

async def check_tenant_rate_limit(tenant_id: str, max_requests: int = 100, window_seconds: int = 60):
    current_time = time.time()
    clear_before = current_time - window_seconds
    key = f"rate_limit:{tenant_id}"

    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.zremrangebyscore(key, 0, clear_before)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, window_seconds)
        results = await pipe.execute()

    request_count = results[1]
    if request_count >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for tenant '{tenant_id}'. Limit is {max_requests} requests per {window_seconds}s."
        )
