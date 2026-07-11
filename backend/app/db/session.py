from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


def _create_session_factory():
    settings = get_settings()
    _engine = create_async_engine(settings.DATABASE_URL, echo=False)
    return _engine, async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


try:
    _engine, AsyncSessionLocal = _create_session_factory()
except Exception:
    _engine = None
    AsyncSessionLocal = None


def get_engine():
    return _engine


async def get_db():
    global _engine, AsyncSessionLocal
    if AsyncSessionLocal is None:
        _engine, AsyncSessionLocal = _create_session_factory()
    async with AsyncSessionLocal() as session:
        yield session
