from sqlalchemy import select

from app.models.company import Company
from app.repositories.base import RepositoryBase
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyRepository(
    RepositoryBase[Company, CompanyCreate, CompanyUpdate]
):
    async def get_by_name(self, name: str) -> Company | None:
        stmt = select(Company).where(Company.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_name(self, name: str, limit: int = 10) -> list[Company]:
        stmt = (
            select(Company)
            .where(Company.name.ilike(f"%{name}%"))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
