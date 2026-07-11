"""init models

Revision ID: 0001
Revises:
Create Date: 2026-07-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS public"))

    op.execute("CREATE TYPE employment_type AS ENUM ('full_time', 'part_time', 'contract', 'freelance', 'internship')")
    op.execute("CREATE TYPE experience_level AS ENUM ('intern', 'entry', 'junior', 'mid', 'senior', 'staff', 'lead', 'principal')")
    op.execute("CREATE TYPE source AS ENUM ('linkedin', 'indeed', 'computrabajo', 'getonboard', 'glassdoor', 'remoteok', 'wellfound', 'greenhouse', 'lever', 'other')")

    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )
    op.create_index("ix_companies_name", "companies", ["name"])

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("salary_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("salary_max", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("employment_type", sa.Enum("full_time", "part_time", "contract", "freelance", "internship", name="employment_type", create_type=False), nullable=True),
        sa.Column("experience_level", sa.Enum("intern", "entry", "junior", "mid", "senior", "staff", "lead", "principal", name="experience_level", create_type=False), nullable=True),
        sa.Column("source", sa.Enum("linkedin", "indeed", "computrabajo", "getonboard", "glassdoor", "remoteok", "wellfound", "greenhouse", "lever", "other", name="source", create_type=False), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(1000), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_data", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )
    op.create_index("ix_jobs_company_id", "jobs", ["company_id"])
    op.create_index("ix_jobs_source_scraped_at", "jobs", ["source", "scraped_at"])
    op.create_unique_constraint("uq_job_source_external_id", "jobs", ["source", "external_id"])


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_table("companies")
    op.execute("DROP TYPE source")
    op.execute("DROP TYPE experience_level")
    op.execute("DROP TYPE employment_type")
