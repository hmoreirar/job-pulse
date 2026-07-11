import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.company import Company
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter()


def get_company_repo(db: AsyncSession = Depends(get_db)) -> CompanyRepository:
    return CompanyRepository(Company, db)


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    repo: CompanyRepository = Depends(get_company_repo),
):
    return await repo.create(data)


@router.get("", response_model=list[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    repo: CompanyRepository = Depends(get_company_repo),
):
    return await repo.get_multi(skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: uuid.UUID,
    repo: CompanyRepository = Depends(get_company_repo),
):
    company = await repo.get(company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdate,
    repo: CompanyRepository = Depends(get_company_repo),
):
    company = await repo.get(company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await repo.update(company, data)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: uuid.UUID,
    repo: CompanyRepository = Depends(get_company_repo),
):
    deleted = await repo.delete(company_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
