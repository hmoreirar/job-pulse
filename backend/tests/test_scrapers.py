import json
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models.job import ExperienceLevel, Source
from app.scrapers.getonboard import (
    GetOnBoardScraper,
    _build_company_map,
    _strip_html,
)

SAMPLE_JOB = {
    "id": "desarrollador-python-empresa-tech-santiago",
    "type": "job",
    "attributes": {
        "title": "Desarrollador Python",
        "description": "<p>Buscamos un <strong>Python Developer</strong> con experiencia.</p>",
        "min_salary": 3000,
        "max_salary": 5000,
        "remote": False,
        "remote_modality": "no_remote",
        "countries": ["Chile"],
        "published_at": 1783635343,
        "seniority": {"data": {"id": 3, "type": "seniority"}},
        "company": {"data": {"id": "user-218", "type": "company"}},
    },
    "links": {
        "public_url": "https://www.getonbrd.com/jobs/desarrollador-python-empresa-tech-santiago"
    },
    "_company_name": "Empresa Tech",
}

SAMPLE_SENIORITIES = {
    "data": [
        {"id": 1, "type": "seniority", "attributes": {"name": "Intern"}},
        {"id": 2, "type": "seniority", "attributes": {"name": "Junior"}},
        {"id": 3, "type": "seniority", "attributes": {"name": "Semi Senior"}},
        {"id": 4, "type": "seniority", "attributes": {"name": "Senior"}},
    ]
}

INCLUDED_COMPANIES = [
    {
        "id": "user-218",
        "type": "company",
        "attributes": {"name": "Empresa Tech"},
    }
]


class TestStripHtml:
    def test_removes_tags(self):
        assert _strip_html("<p>Hola <b>mundo</b></p>") == "Hola mundo"

    def test_handles_none(self):
        assert _strip_html(None) is None

    def test_collapses_whitespace(self):
        result = _strip_html("<div>  foo  \n  bar  </div>")
        assert result == "foo bar"

    def test_unescapes_entities(self):
        assert _strip_html("<p>Foo &amp; Bar</p>") == "Foo & Bar"


class TestBuildCompanyMap:
    def test_builds_map_from_included(self):
        result = _build_company_map(INCLUDED_COMPANIES)
        assert result == {"user-218": "Empresa Tech"}

    def test_returns_empty_dict_for_empty_list(self):
        assert _build_company_map([]) == {}

    def test_skips_non_company_types(self):
        included = [
            {"id": "1", "type": "company", "attributes": {"name": "ACME"}},
            {"id": "99", "type": "category", "attributes": {"name": "Tech"}},
        ]
        result = _build_company_map(included)
        assert result == {"1": "ACME"}


class TestGetOnBoardNormalize:
    def test_normalize_full_job(self):
        scraper = GetOnBoardScraper()
        scraper._seniority_map = {3: ExperienceLevel.MID}

        parsed = scraper.parse([SAMPLE_JOB])
        result = scraper.normalize(parsed)

        assert len(result) == 1
        job = result[0]

        assert job.title == "Desarrollador Python"
        assert job.company_name == "Empresa Tech"
        assert "Python Developer" in job.description
        assert job.description is not None
        assert "<strong>" not in job.description
        assert job.location == "Chile"
        assert job.salary_min == Decimal("3000.00")
        assert job.salary_max == Decimal("5000.00")
        assert job.currency is None
        assert job.employment_type is None
        assert job.experience_level == ExperienceLevel.MID
        assert job.source == Source.GETONBOARD
        assert job.external_id == "desarrollador-python-empresa-tech-santiago"
        assert job.source_url == "https://www.getonbrd.com/jobs/desarrollador-python-empresa-tech-santiago"
        assert job.posted_at == datetime.fromtimestamp(1783635343, tz=timezone.utc)
        assert job.raw_data is not None

    def test_normalize_remote_job(self):
        remote_job = dict(SAMPLE_JOB)
        remote_job["attributes"] = dict(SAMPLE_JOB["attributes"])
        remote_job["attributes"]["remote"] = True
        remote_job["attributes"]["remote_modality"] = "remote"
        remote_job["attributes"]["countries"] = []

        scraper = GetOnBoardScraper()
        scraper._seniority_map = {}

        result = scraper.normalize(scraper.parse([remote_job]))
        assert result[0].location == "Remote"

    def test_normalize_hybrid_job(self):
        hybrid_job = dict(SAMPLE_JOB)
        hybrid_job["attributes"] = dict(SAMPLE_JOB["attributes"])
        hybrid_job["attributes"]["remote_modality"] = "hybrid"

        scraper = GetOnBoardScraper()
        scraper._seniority_map = {}

        result = scraper.normalize(scraper.parse([hybrid_job]))
        assert "Hybrid" in result[0].location

    def test_skips_job_without_title(self):
        no_title = dict(SAMPLE_JOB)
        no_title["attributes"] = dict(SAMPLE_JOB["attributes"])
        no_title["attributes"]["title"] = ""

        scraper = GetOnBoardScraper()
        scraper._seniority_map = {}

        result = scraper.normalize(scraper.parse([no_title]))
        assert len(result) == 0

    def test_normalize_without_seniority(self):
        no_seniority = dict(SAMPLE_JOB)
        no_seniority["attributes"] = dict(SAMPLE_JOB["attributes"])
        no_seniority["attributes"]["seniority"] = {"data": None}

        scraper = GetOnBoardScraper()
        scraper._seniority_map = {}

        result = scraper.normalize(scraper.parse([no_seniority]))
        assert result[0].experience_level is None

    def test_normalize_unknown_company(self):
        unknown = dict(SAMPLE_JOB)
        unknown.pop("_company_name")

        scraper = GetOnBoardScraper()
        scraper._seniority_map = {}

        result = scraper.normalize(scraper.parse([unknown]))
        assert result[0].company_name == "Unknown"

    def test_seniority_mapping(self):
        scraper = GetOnBoardScraper()
        scraper._seniority_map = {
            1: ExperienceLevel.INTERN,
            2: ExperienceLevel.JUNIOR,
            3: ExperienceLevel.MID,
            4: ExperienceLevel.SENIOR,
        }

        cases = [
            (1, ExperienceLevel.INTERN),
            (2, ExperienceLevel.JUNIOR),
            (3, ExperienceLevel.MID),
            (4, ExperienceLevel.SENIOR),
            (99, None),
        ]

        for seniority_id, expected in cases:
            job = dict(SAMPLE_JOB)
            job["attributes"] = dict(SAMPLE_JOB["attributes"])
            job["attributes"]["seniority"] = {"data": {"id": seniority_id, "type": "seniority"}}
            result = scraper.normalize(scraper.parse([job]))
            assert result[0].experience_level == expected, f"Failed for id {seniority_id}"

    def test_parse_filters_non_jobs(self):
        items = [
            {"type": "job", "id": "job-1"},
            {"type": "company", "id": "comp-1"},
            {"type": "job", "id": "job-2"},
        ]
        scraper = GetOnBoardScraper()
        result = scraper.parse(items)
        assert len(result) == 2
        assert all(j["type"] == "job" for j in result)


class TestSalaryParsing:
    def test_salary_as_none_when_missing(self):
        job_no_salary = dict(SAMPLE_JOB)
        job_no_salary["attributes"] = dict(SAMPLE_JOB["attributes"])
        job_no_salary["attributes"]["min_salary"] = None
        job_no_salary["attributes"]["max_salary"] = None

        scraper = GetOnBoardScraper()
        scraper._seniority_map = {}
        result = scraper.normalize(scraper.parse([job_no_salary]))
        assert result[0].salary_min is None
        assert result[0].salary_max is None

    def test_salary_from_integer(self):
        scraper = GetOnBoardScraper()
        scraper._seniority_map = {}
        result = scraper.normalize(scraper.parse([SAMPLE_JOB]))
        assert result[0].salary_min == Decimal("3000.00")
        assert result[0].salary_max == Decimal("5000.00")


@pytest.mark.asyncio
async def test_upsert_inserts_new_job(monkeypatch):
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.models import target_metadata
    from app.scrapers.service import ScraperService
    from app.scrapers.schemas import JobData

    engine = create_async_engine(
        "postgresql+psycopg://jobpulse:jobpulse@localhost:5432/jobpulse",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(target_metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_factory() as session:
        service = ScraperService(session)

        data = [
            JobData(
                title="Test Job",
                company_name="Test Corp",
                source=Source.GETONBOARD,
                external_id="test-001",
            )
        ]

        await service.persist(data)

        jobs = await service.job_repo.get_multi()
        assert len(jobs) == 1
        assert jobs[0].title == "Test Job"
        assert jobs[0].company.name == "Test Corp"

    async with engine.begin() as conn:
        await conn.run_sync(target_metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_upsert_updates_existing_job(monkeypatch):
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.models import target_metadata
    from app.scrapers.service import ScraperService
    from app.scrapers.schemas import JobData

    engine = create_async_engine(
        "postgresql+psycopg://jobpulse:jobpulse@localhost:5432/jobpulse",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(target_metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_factory() as session:
        service = ScraperService(session)

        await service.persist([
            JobData(
                title="Original Title",
                company_name="Update Corp",
                source=Source.GETONBOARD,
                external_id="update-001",
            )
        ])

    async with session_factory() as session:
        service = ScraperService(session)
        await service.persist([
            JobData(
                title="Updated Title",
                company_name="Update Corp",
                source=Source.GETONBOARD,
                external_id="update-001",
            )
        ])

    async with session_factory() as session:
        service = ScraperService(session)
        jobs = await service.job_repo.get_multi()
        assert len(jobs) == 1
        assert jobs[0].title == "Updated Title"

    async with engine.begin() as conn:
        await conn.run_sync(target_metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_upsert_reuses_existing_company(monkeypatch):
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.models import target_metadata
    from app.scrapers.service import ScraperService
    from app.scrapers.schemas import JobData

    engine = create_async_engine(
        "postgresql+psycopg://jobpulse:jobpulse@localhost:5432/jobpulse",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(target_metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_factory() as session:
        service = ScraperService(session)

        await service.persist([
            JobData(
                title="Job A",
                company_name="Shared Corp",
                source=Source.GETONBOARD,
                external_id="shared-001",
            ),
            JobData(
                title="Job B",
                company_name="Shared Corp",
                source=Source.GETONBOARD,
                external_id="shared-002",
            ),
        ])

        companies = await service.company_repo.get_multi()
        assert len(companies) == 1

    async with engine.begin() as conn:
        await conn.run_sync(target_metadata.drop_all)

    await engine.dispose()
