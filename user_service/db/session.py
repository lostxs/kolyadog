from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    execution_options={"isolation_level": "AUTOCOMMIT"},
)

# create session for the interaction with database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
