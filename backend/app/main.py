from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import Settings, get_settings
import app.db.session as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = app.state.settings
    engine = db.create_engine(settings)
    db.engine = engine
    db.async_session = db.create_session_factory(engine)
    yield
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
