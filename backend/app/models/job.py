import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class ExperienceLevel(StrEnum):
    INTERN = "intern"
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    LEAD = "lead"
    PRINCIPAL = "principal"


class Source(StrEnum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    COMPUTRABAJO = "computrabajo"
    GETONBOARD = "getonboard"
    GLASSDOOR = "glassdoor"
    REMOTEOK = "remoteok"
    WELLFOUNDED = "wellfound"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    OTHER = "other"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary_min: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    salary_max: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    employment_type: Mapped[EmploymentType | None] = mapped_column(
        Enum(EmploymentType, name="employment_type", create_constraint=True),
        nullable=True,
    )
    experience_level: Mapped[ExperienceLevel | None] = mapped_column(
        Enum(ExperienceLevel, name="experience_level", create_constraint=True),
        nullable=True,
    )
    source: Mapped[Source] = mapped_column(
        Enum(Source, name="source", create_constraint=True),
        nullable=False,
    )
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scraped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True,
        comment="Uso exclusivo para almacenar la respuesta original del scraper. No debe utilizarse como fuente principal para consultas de la aplicacion.",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    company: Mapped["Company"] = relationship(  # noqa: F821
        back_populates="jobs"
    )

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_job_source_external_id"),
        Index("ix_job_source_scraped_at", "source", "scraped_at"),
    )
