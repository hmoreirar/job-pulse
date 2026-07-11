from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import Settings, get_settings
from app.db.session import get_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine = get_engine()
    if engine is not None:
        await engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.include_router(api_router, prefix="/api/v1")
    return app
