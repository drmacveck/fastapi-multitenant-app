from fastapi import Request, HTTPException, status
from redis_client import get_redis_client

async def check_rate_limit(request: Request):
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        return

    redis = get_redis_client()
    try:
        key = f"rate_limit:{tenant_id}"
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, 60)

        if current > 10:  # Adjust window/threshold according to your test rules
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
    finally:
        await redis.aclose()
