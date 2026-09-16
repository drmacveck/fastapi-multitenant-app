import os
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

class DynamicRedisClient:
    """Proxy object that creates a Redis client bound to the current running event loop."""
    @property
    def client(self):
        return redis.from_url(REDIS_URL, decode_responses=True)

    def __getattr__(self, name):
        return getattr(self.client, name)

redis_client = DynamicRedisClient()

async def get_redis():
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()
