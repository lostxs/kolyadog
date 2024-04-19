from typing import Optional

from redis.asyncio import Redis

import settings

redis_pool: Optional[Redis] = None


async def get_redis_auth_pool() -> Redis:
    global redis_pool
    if redis_pool is None:
        redis_pool = await Redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True, db=0
        )
    return redis_pool
