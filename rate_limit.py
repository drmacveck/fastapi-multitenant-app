import time

from fastapi import HTTPException, status

from redis_client import redis_client


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
            detail=f"Rate limit exceeded for tenant '{tenant_id}'."
        )
