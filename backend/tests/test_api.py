import asyncio
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.models import target_metadata
from tests.config import TEST_DATABASE_URL


@pytest.fixture
def clean_db():
    def _clean() -> None:
        async def run() -> None:
            engine = create_async_engine(TEST_DATABASE_URL)
            async with engine.begin() as conn:
                await conn.run_sync(target_metadata.create_all)
                await conn.execute(text("TRUNCATE TABLE jobs, companies"))
            await engine.dispose()

        asyncio.run(run())

    _clean()
    yield
    _clean()


class TestCompanyAPI:
    def test_create_company_returns_201(self, client, clean_db):
        resp = client.post("/api/v1/companies", json={"name": "Tech Corp"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Tech Corp"
        assert "id" in data

    def test_list_companies(self, client, clean_db):
        client.post("/api/v1/companies", json={"name": "Alpha Corp"})
        client.post("/api/v1/companies", json={"name": "Beta Corp"})
        resp = client.get("/api/v1/companies")
        assert resp.status_code == 200
        names = [c["name"] for c in resp.json()]
        assert "Alpha Corp" in names
        assert "Beta Corp" in names

    def test_get_company_by_id(self, client, clean_db):
        created = client.post("/api/v1/companies", json={"name": "Gamma Corp"}).json()
        resp = client.get(f"/api/v1/companies/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Gamma Corp"

    def test_get_company_returns_404(self, client, clean_db):
        resp = client.get(f"/api/v1/companies/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_update_company(self, client, clean_db):
        created = client.post("/api/v1/companies", json={"name": "Delta Corp"}).json()
        resp = client.patch(
            f"/api/v1/companies/{created['id']}", json={"location": "Remote"}
        )
        assert resp.status_code == 200
        assert resp.json()["location"] == "Remote"

    def test_update_company_returns_404(self, client, clean_db):
        resp = client.patch(f"/api/v1/companies/{uuid.uuid4()}", json={"name": "X"})
        assert resp.status_code == 404

    def test_delete_company(self, client, clean_db):
        created = client.post("/api/v1/companies", json={"name": "Epsilon Corp"}).json()
        resp = client.delete(f"/api/v1/companies/{created['id']}")
        assert resp.status_code == 204

    def test_delete_company_returns_404(self, client, clean_db):
        resp = client.delete(f"/api/v1/companies/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestJobAPI:
    def _create_company(self, client, name="JobCo"):
        return client.post("/api/v1/companies", json={"name": name}).json()

    def _create_job(self, client, company_id, title="API Job", **overrides):
        payload = {
            "company_id": str(company_id),
            "title": title,
            "description": "Test description",
            "location": "Remote",
            "salary_min": 1000,
            "salary_max": 5000,
            "currency": "USD",
            "employment_type": "full_time",
            "experience_level": "mid",
            "source": "getonboard",
            "external_id": str(uuid.uuid4()),
            "is_active": True,
        }
        payload.update(overrides)
        return client.post("/api/v1/jobs", json=payload)

    def test_create_job_returns_201(self, client, clean_db):
        company = self._create_company(client)
        resp = self._create_job(client, company["id"])
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "API Job"
        assert data["source"] == "getonboard"

    def test_get_job_by_id(self, client, clean_db):
        company = self._create_company(client)
        created = self._create_job(client, company["id"]).json()
        resp = client.get(f"/api/v1/jobs/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "API Job"

    def test_get_job_returns_404(self, client, clean_db):
        resp = client.get(f"/api/v1/jobs/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_update_job(self, client, clean_db):
        company = self._create_company(client)
        created = self._create_job(client, company["id"]).json()
        resp = client.patch(f"/api/v1/jobs/{created['id']}", json={"title": "Renamed"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Renamed"

    def test_update_job_returns_404(self, client, clean_db):
        resp = client.patch(f"/api/v1/jobs/{uuid.uuid4()}", json={"title": "X"})
        assert resp.status_code == 404

    def test_delete_job(self, client, clean_db):
        company = self._create_company(client)
        created = self._create_job(client, company["id"]).json()
        resp = client.delete(f"/api/v1/jobs/{created['id']}")
        assert resp.status_code == 204

    def test_delete_job_returns_404(self, client, clean_db):
        resp = client.delete(f"/api/v1/jobs/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_filter_by_salary_min(self, client, clean_db):
        company = self._create_company(client, "SalaryCo")
        self._create_job(client, company["id"], title="Low Pay", salary_min=1000, salary_max=2000)
        self._create_job(client, company["id"], title="High Pay", salary_min=90000, salary_max=120000)
        resp = client.get("/api/v1/jobs?salary_min=50000")
        assert resp.status_code == 200
        titles = [j["title"] for j in resp.json()["items"]]
        assert "High Pay" in titles
        assert "Low Pay" not in titles

    def test_filter_by_salary_max(self, client, clean_db):
        company = self._create_company(client, "SalaryCo")
        self._create_job(client, company["id"], title="Low Pay", salary_min=1000, salary_max=2000)
        self._create_job(client, company["id"], title="High Pay", salary_min=90000, salary_max=120000)
        resp = client.get("/api/v1/jobs?salary_max=10000")
        assert resp.status_code == 200
        titles = [j["title"] for j in resp.json()["items"]]
        assert "Low Pay" in titles
        assert "High Pay" not in titles

    def test_filter_by_posted_after(self, client, clean_db):
        company = self._create_company(client, "PostedCo")
        self._create_job(
            client,
            company["id"],
            title="Old Job",
            posted_at="2024-01-01T00:00:00Z",
        )
        self._create_job(
            client,
            company["id"],
            title="New Job",
            posted_at="2025-01-01T00:00:00Z",
        )
        resp = client.get("/api/v1/jobs?posted_after=2024-06-01T00:00:00Z")
        assert resp.status_code == 200
        titles = [j["title"] for j in resp.json()["items"]]
        assert "New Job" in titles
        assert "Old Job" not in titles
