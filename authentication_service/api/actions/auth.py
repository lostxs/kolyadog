import json
import logging
import settings
import jwt
from datetime import datetime
from typing import Union, Tuple, Optional
from uuid import UUID

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        result = await session.execute(select(AuthUser).where(AuthUser.email == email)) # noqa
        user = result.scalars().first()
        return user


async def check_token_expiration(user_id: UUID) -> bool:
    redis = await get_redis_auth_pool()
    user_key = f"user_id:{user_id}"
    session_data = await redis.get(user_key)
    if session_data is None:
        return False
    session_info = json.loads(session_data)
    expiration_time_str = session_info['exp']
    expiration_time = datetime.strptime(expiration_time_str, "%Y-%m-%d %H:%M:%S")
    expiration_time = expiration_time.replace(tzinfo=settings.ekb_timezone)
    current_time = datetime.now(settings.ekb_timezone)

    if current_time > expiration_time:
        await redis.delete(user_key)
        return False
    return True


async def verify_token(token: str) -> Tuple[Optional[UUID], bool]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = UUID(payload.get("sub"))
        if user_id is None:
            return None, False

        redis = await get_redis_auth_pool()
        if await redis.get(f"user_id:{user_id}"):
            return user_id, True
        else:
            return None, False
    except (jwt.PyJWTError, ValueError) as e:
        logging.error(f"Token verification error: {e}")
        return None, False
