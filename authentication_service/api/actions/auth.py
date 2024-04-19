import json
import logging
from datetime import datetime
from typing import Union
from uuid import UUID

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from db.models import AuthUser
from db.redis import get_redis_auth_pool
from hashing import Hasher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def authenticate_user(
    email: str, password: str, db: AsyncSession
) -> Union[AuthUser, None]:
    user = await _get_user_by_email_for_auth(email=email, session=db)
    if user is None or not user.is_active:
        return
    if not Hasher.verify_password(password, user.hashed_password):
        return
    return user


async def _get_user_by_email_for_auth(email: str, session: AsyncSession) -> Union[AuthUser, None]:
    async with session.begin():
        result = await session.execute(select(AuthUser).where(AuthUser.email == email))
        user = result.scalars().first()
        return user


async def check_token_expiration(user_id: UUID) -> bool:
    redis = await get_redis_auth_pool()
    user_key = f"user_id:{user_id}"
    session_data = await redis.get(user_key)
    if session_data is None:
        return False
    session_info = json.loads(session_data)
    if datetime.now(settings.ekb_timezone).timestamp() > float(session_info['exp']):
        await redis.delete(user_key)
        return False
    return True
