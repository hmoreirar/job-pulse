import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from tests.config import TEST_DATABASE_URL


@pytest.mark.asyncio
async def test_database_connection():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
    await engine.dispose()
