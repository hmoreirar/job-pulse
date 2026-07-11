import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.job import Job, Source
from app.repositories.job import JobRepository
from app.schemas.job import JobCreate, JobList, JobResponse, JobUpdate

router = APIRouter()


def get_job_repo(db: AsyncSession = Depends(get_db)) -> JobRepository:
    return JobRepository(Job, db)


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    repo: JobRepository = Depends(get_job_repo),
):
    return await repo.create(data)


@router.get("", response_model=JobList)
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    source: Source | None = Query(None),
    active_only: bool = Query(False),
    repo: JobRepository = Depends(get_job_repo),
):
    if active_only:
        items = await repo.get_active(skip=skip, limit=limit)
    elif source:
        items = await repo.get_by_source(source, skip=skip, limit=limit)
    else:
        items = await repo.get_multi(skip=skip, limit=limit)
    total = await repo.count()
    return JobList(items=items, total=total)


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
