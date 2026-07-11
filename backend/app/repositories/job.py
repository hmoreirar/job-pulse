import uuid
from datetime import datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.models.job import Job, Source
from app.repositories.base import RepositoryBase
from app.schemas.job import JobCreate, JobSearchFilters, JobUpdate


SORT_COLUMN_MAP = {
    "posted_at": Job.posted_at,
    "scraped_at": Job.scraped_at,
    "created_at": Job.created_at,
    "salary_min": Job.salary_min,
    "salary_max": Job.salary_max,
    "title": Job.title,
}


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

    async def search(self, filters: JobSearchFilters) -> tuple[list[Job], int]:
        conditions: list = []
        needs_company_join = False

        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    Job.title.ilike(pattern),
                    Job.description.ilike(pattern),
                    Company.name.ilike(pattern),
                )
            )
            needs_company_join = True

        if filters.company_id is not None:
            conditions.append(Job.company_id == filters.company_id)

        if filters.source is not None:
            conditions.append(Job.source == filters.source)

        if filters.employment_type is not None:
            conditions.append(Job.employment_type == filters.employment_type)

        if filters.experience_level is not None:
            conditions.append(Job.experience_level == filters.experience_level)

        if filters.is_active is not None:
            conditions.append(Job.is_active == filters.is_active)

        if filters.location:
            conditions.append(Job.location.ilike(f"%{filters.location}%"))

        # Count query
        count_stmt = select(func.count()).select_from(Job)
        if needs_company_join:
            count_stmt = count_stmt.join(Company)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()

        # Data query
        stmt = select(Job).options(selectinload(Job.company))
        if needs_company_join:
            stmt = stmt.join(Company)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Sort
        if filters.sort:
            col = SORT_COLUMN_MAP[filters.sort]
            col = col.desc() if filters.order == "desc" else col.asc()
            stmt = stmt.order_by(col)

        # Pagination
        offset = (filters.page - 1) * filters.page_size
        stmt = stmt.offset(offset).limit(filters.page_size)

        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total
