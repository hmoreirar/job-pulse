
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.company import Company
from app.models.job import Job, Source
from app.repositories.company import CompanyRepository
from app.repositories.job import JobRepository
from app.schemas.company import CompanyCreate
from app.schemas.job import JobCreate


@pytest.fixture
async def engine():
    engine = create_async_engine(
        "postgresql+psycopg://jobpulse:jobpulse@localhost:5432/jobpulse",
        echo=False,
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def setup_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Company.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Company.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_company(session, setup_db):
    repo = CompanyRepository(Company, session)
    data = CompanyCreate(name="Test Corp", location="Remote")
    company = await repo.create(data)

    assert company.id is not None
    assert company.name == "Test Corp"
    assert company.location == "Remote"


@pytest.mark.asyncio
async def test_get_company(session, setup_db):
    repo = CompanyRepository(Company, session)
    data = CompanyCreate(name="Test Corp", location="Remote")
    created = await repo.create(data)

    found = await repo.get(created.id)
    assert found is not None
    assert found.name == "Test Corp"


@pytest.mark.asyncio
async def test_get_multi_companies(session, setup_db):
    repo = CompanyRepository(Company, session)
    await repo.create(CompanyCreate(name="Company A"))
    await repo.create(CompanyCreate(name="Company B"))

    companies = await repo.get_multi()
    assert len(companies) >= 2


@pytest.mark.asyncio
async def test_count_companies(session, setup_db):
    repo = CompanyRepository(Company, session)
    await repo.create(CompanyCreate(name="Company A"))
    await repo.create(CompanyCreate(name="Company B"))

    count = await repo.count()
    assert count >= 2


@pytest.mark.asyncio
async def test_delete_company(session, setup_db):
    repo = CompanyRepository(Company, session)
    company = await repo.create(CompanyCreate(name="To Delete"))

    deleted = await repo.delete(company.id)
    assert deleted is True

    found = await repo.get(company.id)
    assert found is None


@pytest.mark.asyncio
async def test_get_by_name(session, setup_db):
    repo = CompanyRepository(Company, session)
    await repo.create(CompanyCreate(name="Unique Corp"))

    found = await repo.get_by_name("Unique Corp")
    assert found is not None
    assert found.name == "Unique Corp"


@pytest.mark.asyncio
async def test_search_by_name(session, setup_db):
    repo = CompanyRepository(Company, session)
    await repo.create(CompanyCreate(name="Acme Corp"))
    await repo.create(CompanyCreate(name="Acme Industries"))

    results = await repo.search_by_name("Acme")
    assert len(results) >= 2


@pytest.mark.asyncio
async def test_create_job(session, setup_db):
    company_repo = CompanyRepository(Company, session)
    company = await company_repo.create(CompanyCreate(name="JobCo"))

    job_repo = JobRepository(Job, session)
    data = JobCreate(
        company_id=company.id,
        title="Software Engineer",
        source=Source.OTHER,
    )
    job = await job_repo.create(data)

    assert job.id is not None
    assert job.title == "Software Engineer"
    assert job.source == Source.OTHER
    assert job.is_active is True


@pytest.mark.asyncio
async def test_get_by_source_external_id(session, setup_db):
    company_repo = CompanyRepository(Company, session)
    company = await company_repo.create(CompanyCreate(name="SrcCo"))

    job_repo = JobRepository(Job, session)
    await job_repo.create(
        JobCreate(
            company_id=company.id,
            title="Dev",
            source=Source.LINKEDIN,
            external_id="ext-123",
        )
    )

    found = await job_repo.get_by_source_external_id(Source.LINKEDIN, "ext-123")
    assert found is not None
    assert found.title == "Dev"


@pytest.mark.asyncio
async def test_get_active_jobs(session, setup_db):
    company_repo = CompanyRepository(Company, session)
    company = await company_repo.create(CompanyCreate(name="ActiveCo"))

    job_repo = JobRepository(Job, session)
    await job_repo.create(
        JobCreate(company_id=company.id, title="Active", source=Source.OTHER)
    )
    inactive = await job_repo.create(
        JobCreate(company_id=company.id, title="Inactive", source=Source.OTHER, is_active=False)
    )

    active_jobs = await job_repo.get_active()
    active_titles = [j.title for j in active_jobs]
    assert "Active" in active_titles
    assert "Inactive" not in active_titles


@pytest.mark.asyncio
async def test_get_by_company(session, setup_db):
    company_repo = CompanyRepository(Company, session)
    c1 = await company_repo.create(CompanyCreate(name="Co1"))
    c2 = await company_repo.create(CompanyCreate(name="Co2"))

    job_repo = JobRepository(Job, session)
    await job_repo.create(JobCreate(company_id=c1.id, title="Role A", source=Source.REMOTEOK))
    await job_repo.create(JobCreate(company_id=c1.id, title="Role B", source=Source.REMOTEOK))
    await job_repo.create(JobCreate(company_id=c2.id, title="Role C", source=Source.REMOTEOK))

    c1_jobs = await job_repo.get_by_company(c1.id)
    assert len(c1_jobs) == 2


@pytest.mark.asyncio
async def test_get_by_source(session, setup_db):
    company_repo = CompanyRepository(Company, session)
    company = await company_repo.create(CompanyCreate(name="SrcCo"))

    job_repo = JobRepository(Job, session)
    await job_repo.create(JobCreate(company_id=company.id, title="LIn", source=Source.LINKEDIN))
    await job_repo.create(JobCreate(company_id=company.id, title="Ind", source=Source.INDEED))

    linkedin_jobs = await job_repo.get_by_source(Source.LINKEDIN)
    assert len(linkedin_jobs) == 1
    assert linkedin_jobs[0].title == "LIn"
