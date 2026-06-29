import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_connection(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://jobpulse:jobpulse@localhost:5432/jobpulse",
    )
    from app.db.session import create_engine

    engine = create_engine()
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
    await engine.dispose()
