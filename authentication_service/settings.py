from zoneinfo import ZoneInfo
from envparse import Env

env = Env()

ekb_timezone = ZoneInfo("Asia/Yekaterinburg")


REDIS_URL = env.str("REDIS_URL", default="redis://localhost:6379")

DATABASE_URL = env.str(
    "DATABASE_URL", default="postgresql+asyncpg://postgres:postgres@localhost:5434/auth_db"
)

SECRET_KEY = env.str("SECRET_KEY", default="My_secret")
ALGORITHM: str = env.str("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
