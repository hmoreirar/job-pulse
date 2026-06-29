import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def client():
    settings = Settings(
        ENVIRONMENT="test",
        DATABASE_URL="postgresql+psycopg://test:test@localhost:5432/test",
    )
    app = create_app(settings=settings)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)
