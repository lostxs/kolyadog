from envparse import Env
from zoneinfo import ZoneInfo

env = Env()

ekb_timezone = ZoneInfo("Asia/Yekaterinburg")

DATABASE_URL = env.str(
    "DATABASE_URL", default="postgresql+asyncpg://postgres:postgres@localhost:5435/message_db"
)
MESSAGE_REDIS_URL = env.str("REDIS_URL", default="redis://localhost:6380")

AUTH_REDIS_URL = env.str("REDIS_URL", default="redis://localhost:6379")
