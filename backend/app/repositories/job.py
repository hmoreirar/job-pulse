import uuid
from datetime import datetime

from sqlalchemy import select, and_

from app.models.job import Job, Source
from app.repositories.base import RepositoryBase
from app.schemas.job import JobCreate, JobUpdate


class JobRepository(RepositoryBase[Job, JobCreate, JobUpdate]):
    async def get_by_company(self, company_id: uuid.UUID) -> list[Job]:
        stmt = select(Job).where(Job.company_id == company_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_source(
        self, source: Source, skip: int = 0, limit: int = 100
    ) -> list[Job]:
        stmt = (
            select(Job)
            .where(Job.source == source)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active(self, skip: int = 0, limit: int = 100) -> list[Job]:
        stmt = (
            select(Job)
            .where(Job.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_source_external_id(
        self, source: Source, external_id: str
    ) -> Job | None:
        stmt = select(Job).where(
            and_(Job.source == source, Job.external_id == external_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recently_scraped(
        self, since: datetime, limit: int = 100
    ) -> list[Job]:
        stmt = (
            select(Job)
            .where(Job.scraped_at >= since)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
