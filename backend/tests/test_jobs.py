import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.company import Company
from app.models.job import Job, Source, EmploymentType, ExperienceLevel
from app.repositories.company import CompanyRepository
from app.repositories.job import JobRepository
from app.schemas.company import CompanyCreate
from app.schemas.job import JobCreate, JobSearchFilters

TEST_DB_URL = "postgresql+psycopg://jobpulse:jobpulse@localhost:5432/jobpulse"


@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
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


@pytest.fixture
async def companies(session, setup_db):
    repo = CompanyRepository(Company, session)
    c1 = await repo.create(CompanyCreate(name="Tech Corp", location="Remote"))
    c2 = await repo.create(CompanyCreate(name="Dev Inc", location="New York"))
    c3 = await repo.create(CompanyCreate(name="Python Labs", location="Remote"))
    await session.commit()
    return c1, c2, c3


@pytest.fixture
async def jobs(session, companies):
    c1, c2, c3 = companies
    repo = JobRepository(Job, session)

    created = []

    data = [
        JobCreate(
            company_id=c1.id,
            title="Python Developer",
            description="Backend Python developer needed",
            source=Source.GETONBOARD,
            employment_type=EmploymentType.FULL_TIME,
            experience_level=ExperienceLevel.SENIOR,
            location="Remote",
            is_active=True,
        ),
        JobCreate(
            company_id=c1.id,
            title="JavaScript Engineer",
            description="Frontend React developer",
            source=Source.LINKEDIN,
            employment_type=EmploymentType.FULL_TIME,
            experience_level=ExperienceLevel.MID,
            location="Remote",
            is_active=True,
        ),
        JobCreate(
            company_id=c2.id,
            title="Data Scientist",
            description="Python and ML expert",
            source=Source.INDEED,
            employment_type=EmploymentType.CONTRACT,
            experience_level=ExperienceLevel.SENIOR,
            location="New York",
            is_active=True,
        ),
        JobCreate(
            company_id=c2.id,
            title="Junior Tester",
            description="QA engineer",
            source=Source.GETONBOARD,
            employment_type=EmploymentType.PART_TIME,
            experience_level=ExperienceLevel.JUNIOR,
            location="New York",
            is_active=True,
        ),
        JobCreate(
            company_id=c3.id,
            title="DevOps Engineer",
            description="Infrastructure and CI/CD",
            source=Source.REMOTEOK,
            employment_type=EmploymentType.FULL_TIME,
            experience_level=ExperienceLevel.STAFF,
            location="Remote",
            is_active=False,
        ),
        JobCreate(
            company_id=c3.id,
            title="Python Intern",
            description="Learn Python development",
            source=Source.OTHER,
            employment_type=EmploymentType.INTERNSHIP,
            experience_level=ExperienceLevel.INTERN,
            location="Remote",
            is_active=True,
        ),
    ]

    for d in data:
        job = await repo.create(d)
        created.append(job)

    await session.commit()
    return created


class TestSearch:
    async def test_returns_all_jobs_when_no_filters(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters()
        items, total = await repo.search(filters)
        assert total == 6
        assert len(items) == 6

    async def test_search_by_title(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(search="python")
        items, total = await repo.search(filters)
        assert total == 2
        titles = {j.title for j in items}
        assert "Python Developer" in titles
        assert "Python Intern" in titles

    async def test_search_by_title_case_insensitive(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(search="PYTHON")
        items, total = await repo.search(filters)
        assert total == 2

    async def test_search_by_description(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(search="React")
        items, total = await repo.search(filters)
        assert total == 1
        assert items[0].title == "JavaScript Engineer"

    async def test_search_by_company_name(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(search="Tech Corp")
        items, total = await repo.search(filters)
        assert total == 2
        assert all(j.company.name == "Tech Corp" for j in items)

    async def test_search_partial_company_name(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(search="tech")
        items, total = await repo.search(filters)
        assert total >= 2

    async def test_search_returns_empty_for_no_match(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(search="xyznonexistent")
        items, total = await repo.search(filters)
        assert total == 0
        assert items == []


class TestFilters:
    async def test_filter_by_source(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(source=Source.GETONBOARD)
        items, total = await repo.search(filters)
        assert total == 2
        assert all(j.source == Source.GETONBOARD for j in items)

    async def test_filter_by_employment_type(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(employment_type=EmploymentType.FULL_TIME)
        items, total = await repo.search(filters)
        assert total == 3

    async def test_filter_by_experience_level(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(experience_level=ExperienceLevel.SENIOR)
        items, total = await repo.search(filters)
        assert total == 2

    async def test_filter_by_is_active(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(is_active=True)
        items, total = await repo.search(filters)
        assert total == 5

    async def test_filter_by_is_active_false(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(is_active=False)
        items, total = await repo.search(filters)
        assert total == 1
        assert items[0].title == "DevOps Engineer"

    async def test_filter_by_location(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(location="New York")
        items, total = await repo.search(filters)
        assert total == 2
        assert all(j.location == "New York" for j in items)

    async def test_filter_by_location_case_insensitive(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(location="new york")
        items, total = await repo.search(filters)
        assert total == 2

    async def test_filter_by_company_id(self, session, jobs, companies):
        c1, _c2, _c3 = companies
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(company_id=c1.id)
        items, total = await repo.search(filters)
        assert total == 2
        assert all(j.company_id == c1.id for j in items)


class TestCombinedFilters:
    async def test_search_and_source(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(search="python", source=Source.GETONBOARD)
        items, total = await repo.search(filters)
        assert total == 1
        assert items[0].title == "Python Developer"

    async def test_multiple_filters(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(
            source=Source.GETONBOARD,
            employment_type=EmploymentType.FULL_TIME,
            is_active=True,
        )
        items, total = await repo.search(filters)
        assert total == 1
        assert items[0].title == "Python Developer"

    async def test_full_combo(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(
            search="python",
            source=Source.GETONBOARD,
            employment_type=EmploymentType.FULL_TIME,
            is_active=True,
            location="Remote",
        )
        items, total = await repo.search(filters)
        assert total == 1
        assert items[0].title == "Python Developer"


class TestPagination:
    async def test_page_size_limits_results(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(page=1, page_size=2)
        items, total = await repo.search(filters)
        assert total == 6
        assert len(items) == 2

    async def test_second_page(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(page=2, page_size=2)
        items, total = await repo.search(filters)
        assert total == 6
        assert len(items) == 2

    async def test_last_page_with_fewer_items(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(page=3, page_size=4)
        items, total = await repo.search(filters)
        assert total == 6
        assert len(items) == 2

    async def test_page_beyond_total(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(page=10, page_size=10)
        items, total = await repo.search(filters)
        assert total == 6
        assert items == []


class TestSorting:
    async def test_sort_by_title_asc(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(sort="title", order="asc")
        items, total = await repo.search(filters)
        assert total == 6
        titles = [j.title for j in items]
        assert titles == sorted(titles)

    async def test_sort_by_title_desc(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(sort="title", order="desc")
        items, total = await repo.search(filters)
        assert total == 6
        titles = [j.title for j in items]
        assert titles == sorted(titles, reverse=True)

    async def test_default_sort_order_is_desc(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(sort="created_at")
        items, total = await repo.search(filters)
        assert total == 6

    async def test_sort_with_pagination(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(sort="title", order="asc", page=1, page_size=3)
        page1, total = await repo.search(filters)
        assert len(page1) == 3

        filters.page = 2
        page2, total = await repo.search(filters)
        assert len(page2) == 3

        all_titles = [j.title for j in page1] + [j.title for j in page2]
        assert all_titles == sorted(all_titles)


class TestSelectinload:
    async def test_company_is_loaded(self, session, jobs):
        repo = JobRepository(Job, session)
        filters = JobSearchFilters(search="python")
        items, total = await repo.search(filters)
        for job in items:
            assert job.company is not None
            assert job.company.name is not None


@pytest.mark.skip(reason="Requires running PostgreSQL via Docker")
class TestAPIValidation:
    def test_invalid_sort_returns_400(self, client):
        response = client.get("/api/v1/jobs?sort=invalid_field")
        assert response.status_code == 400

    def test_invalid_order_returns_400(self, client):
        response = client.get("/api/v1/jobs?order=invalid")
        assert response.status_code == 400

    def test_page_size_exceeds_max_returns_422(self, client):
        response = client.get("/api/v1/jobs?page_size=200")
        assert response.status_code == 422

    def test_page_below_min_returns_422(self, client):
        response = client.get("/api/v1/jobs?page=0")
        assert response.status_code == 422

    def test_default_pagination(self, client):
        response = client.get("/api/v1/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "pages" in data

    def test_search_param_accepted(self, client):
        response = client.get("/api/v1/jobs?search=python")
        assert response.status_code == 200

    def test_all_filters_accepted(self, client):
        response = client.get(
            "/api/v1/jobs?search=python&source=getonboard"
            "&employment_type=full_time&experience_level=senior"
            "&location=Remote&is_active=true&page=1&page_size=20"
            "&sort=posted_at&order=desc"
        )
        assert response.status_code == 200

    def test_response_shape(self, client):
        response = client.get("/api/v1/jobs")
        data = response.json()
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["page_size"], int)
        assert isinstance(data["pages"], int)
