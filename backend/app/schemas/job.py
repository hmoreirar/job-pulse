import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from app.models.job import EmploymentType, ExperienceLevel, Source


class JobCreate(BaseModel):
    company_id: uuid.UUID
    title: str
    description: str | None = None
    location: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    currency: str | None = Field(None, max_length=3)
    employment_type: EmploymentType | None = None
    experience_level: ExperienceLevel | None = None
    source: Source
    external_id: str | None = None
    source_url: AnyHttpUrl | None = None
    posted_at: datetime | None = None
    scraped_at: datetime | None = None
    raw_data: dict | None = None
    is_active: bool = True


class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    currency: str | None = Field(None, max_length=3)
    employment_type: EmploymentType | None = None
    experience_level: ExperienceLevel | None = None
    source_url: AnyHttpUrl | None = None
    is_active: bool | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    description: str | None = None
    location: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    currency: str | None = None
    employment_type: EmploymentType | None = None
    experience_level: ExperienceLevel | None = None
    source: Source
    external_id: str | None = None
    source_url: str | None = None
    posted_at: datetime | None = None
    scraped_at: datetime | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime | None = None


class JobList(BaseModel):
    items: list[JobResponse]
    total: int


SORT_FIELDS = frozenset({
    "posted_at",
    "scraped_at",
    "created_at",
    "salary_min",
    "salary_max",
    "title",
})


class JobSearchFilters(BaseModel):
    search: str | None = None
    company_id: uuid.UUID | None = None
    source: Source | None = None
    employment_type: EmploymentType | None = None
    experience_level: ExperienceLevel | None = None
    is_active: bool | None = None
    location: str | None = None
    sort: str | None = None
    order: str = "desc"
    page: int = 1
    page_size: int = 20


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    page_size: int
    pages: int
