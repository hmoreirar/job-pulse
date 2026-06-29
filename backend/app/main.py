from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import Settings


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
