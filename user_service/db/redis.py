from typing import Optional

from redis.asyncio import Redis

from settings import AUTH_REDIS_URL

redis_pool_auth: Optional[Redis] = None


async def get_redis_auth_pool() -> Redis:
    return await Redis.from_url(
        AUTH_REDIS_URL, encoding="utf-8", decode_responses=True, db=0
    )
