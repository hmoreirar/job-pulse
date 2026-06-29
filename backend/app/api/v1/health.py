from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter()


@router.get("")
def health(settings: Settings = Depends(get_settings)):
    return {
        "status": "ok",
        "service": "jobpulse-backend",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }
