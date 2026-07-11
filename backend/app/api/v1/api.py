from fastapi import APIRouter

from app.api.v1 import companies, health, jobs

api_router = APIRouter()

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)
api_router.include_router(
    companies.router,
    prefix="/companies",
    tags=["Companies"],
)
api_router.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["Jobs"],
)
