from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel

from app.models.job import EmploymentType, ExperienceLevel, Source


class JobData(BaseModel):
    title: str
    company_name: str
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
    raw_data: dict[str, Any] | None = None
