import asyncio
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from tests.config import TEST_DATABASE_URL

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.core.config import Settings, get_settings
from app.main import create_app
from app.models import target_metadata


@pytest.fixture(scope="session", autouse=True)
def _schema():
    async def setup() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(target_metadata.create_all)
        await engine.dispose()

    async def teardown() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(target_metadata.drop_all)
        await engine.dispose()

    asyncio.run(setup())
    yield
    asyncio.run(teardown())


@pytest.fixture
def client():
    settings = Settings(
        ENVIRONMENT="test",
        DATABASE_URL=TEST_DATABASE_URL,
    )
    app = create_app(settings=settings)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)
