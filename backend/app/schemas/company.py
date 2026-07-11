import uuid
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    description: str | None = None
    website: str | None = None
    logo_url: AnyHttpUrl | None = None
    location: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    website: str | None = None
    logo_url: AnyHttpUrl | None = None
    location: str | None = None


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    website: str | None = None
    logo_url: str | None = None
    location: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
