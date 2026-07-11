import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.job import Job
from app.repositories.company import CompanyRepository
from app.repositories.job import JobRepository
from app.schemas.company import CompanyCreate
from app.schemas.job import JobCreate
from app.scrapers.schemas import JobData

logger = logging.getLogger(__name__)


class ScraperService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.company_repo = CompanyRepository(Company, db)
        self.job_repo = JobRepository(Job, db)

    async def persist(self, data: list[JobData]) -> None:
        inserted = 0
        updated = 0
        failed = 0

        for item in data:
            try:
                company = await self._resolve_company(item)
                is_new = await self._upsert_job(company.id, item)
                if is_new:
                    inserted += 1
                else:
                    updated += 1
            except Exception:
                logger.exception("Failed to process job: %s", item.title)
                failed += 1

        await self.db.commit()

        logger.info("Inserted: %d  Updated: %d  Failed: %d", inserted, updated, failed)

    async def _resolve_company(self, item: JobData) -> Company:
        company = await self.company_repo.get_by_name(item.company_name)
        if company is not None:
            return company
        create_data = CompanyCreate(name=item.company_name)
        return await self.company_repo.create(create_data)

    async def _upsert_job(self, company_id, item: JobData) -> bool:
        now = datetime.now(timezone.utc)

        existing = None
        if item.external_id:
            existing = await self.job_repo.get_by_source_external_id(
                item.source, item.external_id
            )

        if existing:
            update_data = {
                "title": item.title,
                "description": item.description,
                "location": item.location,
                "salary_min": item.salary_min,
                "salary_max": item.salary_max,
                "currency": item.currency,
                "employment_type": item.employment_type,
                "experience_level": item.experience_level,
                "source_url": item.source_url,
                "posted_at": item.posted_at,
                "scraped_at": now,
                "is_active": True,
            }
            await self.job_repo.update(existing, update_data)
            return False
        else:
            create_data = JobCreate(
                company_id=company_id,
                title=item.title,
                description=item.description,
                location=item.location,
                salary_min=item.salary_min,
                salary_max=item.salary_max,
                currency=item.currency,
                employment_type=item.employment_type,
                experience_level=item.experience_level,
                source=item.source,
                external_id=item.external_id,
                source_url=item.source_url,
                posted_at=item.posted_at,
                scraped_at=now,
                raw_data=item.raw_data,
                is_active=True,
            )
            await self.job_repo.create(create_data)
            return True
