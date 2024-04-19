from zoneinfo import ZoneInfo

from envparse import Env

env = Env()

ekb_timezone = ZoneInfo("Asia/Yekaterinburg")

DATABASE_URL = env.str(
    "DATABASE_URL", default="postgresql+asyncpg://postgres:postgres@localhost:5436/register_db"
)
AUTH_REDIS_URL = env.str("REDIS_URL", default="redis://localhost:6379")
