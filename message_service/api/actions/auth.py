from typing import Optional

from fastapi import HTTPException, Depends, Cookie
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


def query_extractor(q: Optional[str] = None):
    return q


def query_or_cookie_extractor(
    q: str = Depends(query_extractor), last_query: Optional[str] = Cookie(None)
):
    if not q:
        return last_query
    return q


async def authenticate_user_via_redis(token: str, redis_auth: Redis):
    user_id = await redis_auth.get(f"token:{token}")
    if not user_id:
        raise HTTPException(status_code=403, detail="Authentication required")
    return user_id


async def get_user_details_by_id(db: AsyncSession, user_id: str) -> User:
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
