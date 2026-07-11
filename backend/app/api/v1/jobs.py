import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.job import Job, Source, EmploymentType, ExperienceLevel
from app.repositories.job import JobRepository
from app.schemas.job import (
    JobCreate,
    JobListResponse,
    JobResponse,
    JobSearchFilters,
    JobUpdate,
    SORT_FIELDS,
)

router = APIRouter()


def get_job_repo(db: AsyncSession = Depends(get_db)) -> JobRepository:
    return JobRepository(Job, db)


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    repo: JobRepository = Depends(get_job_repo),
):
    return await repo.create(data)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    company_id: uuid.UUID | None = Query(None),
    source: Source | None = Query(None),
    employment_type: EmploymentType | None = Query(None),
    experience_level: ExperienceLevel | None = Query(None),
    is_active: bool | None = Query(None),
    location: str | None = Query(None),
    sort: str | None = Query(None),
    order: str = Query("desc"),
    repo: JobRepository = Depends(get_job_repo),
):
    if sort is not None and sort not in SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort field: '{sort}'. Allowed: {', '.join(sorted(SORT_FIELDS))}",
        )

    if order not in ("asc", "desc"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order: '{order}'. Must be 'asc' or 'desc'.",
        )

    filters = JobSearchFilters(
        search=search,
        company_id=company_id,
        source=source,
        employment_type=employment_type,
        experience_level=experience_level,
        is_active=is_active,
        location=location,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    items, total = await repo.search(filters)
    pages = (total + page_size - 1) // page_size
    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    repo: JobRepository = Depends(get_job_repo),
):
    job = await repo.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID,
    data: JobUpdate,
    repo: JobRepository = Depends(get_job_repo),
):
    job = await repo.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return await repo.update(job, data)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    repo: JobRepository = Depends(get_job_repo),
):
    deleted = await repo.delete(job_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
