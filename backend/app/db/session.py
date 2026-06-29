from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)

from app.core.config import get_settings

engine = None
async_session = None


def create_engine():
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )


def create_session_factory(engine):
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
    )


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
