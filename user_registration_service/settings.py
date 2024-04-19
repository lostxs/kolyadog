from _zoneinfo import ZoneInfo
from envparse import Env

env = Env()

ekb_timezone = ZoneInfo("Asia/Yekaterinburg")


DATABASE_URL = env.str(
    "DATABASE_URL", default="postgresql+asyncpg://postgres:postgres@localhost:5433/register_db"
)

ACTIVATION_CODE_EXPIRE_MINUTES: int = env.int(
    "ACTIVATION_CODE_EXPIRE_MINUTES", default=10
)
