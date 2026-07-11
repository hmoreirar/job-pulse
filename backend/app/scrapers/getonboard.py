import json
import logging
import re
import time
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal
from html import unescape

from app.models.job import ExperienceLevel, Source
from app.scrapers.base import BaseScraper
from app.scrapers.schemas import JobData

logger = logging.getLogger(__name__)

API_BASE = "https://www.getonbrd.com/api/v0"

SENIORITY_MAP: dict[str, ExperienceLevel] = {
    "intern": ExperienceLevel.INTERN,
    "junior": ExperienceLevel.JUNIOR,
    "semi senior": ExperienceLevel.MID,
    "senior": ExperienceLevel.SENIOR,
    "lead": ExperienceLevel.LEAD,
    "principal/arch": ExperienceLevel.PRINCIPAL,
}


def _request(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _strip_html(text: str | None) -> str | None:
    if text is None:
        return None
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return unescape(text)


def _build_company_map(included: list[dict]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for item in included or []:
        if item.get("type") == "company":
            attrs = item.get("attributes", {})
            mapping[str(item["id"])] = attrs.get("name", str(item["id"]))
    return mapping


class GetOnBoardScraper(BaseScraper):
    source = Source.GETONBOARD

    def __init__(self) -> None:
        self._seniority_map: dict[int, ExperienceLevel] | None = None

    def _load_seniorities(self) -> dict[int, ExperienceLevel]:
        if self._seniority_map is not None:
            return self._seniority_map
        data = _request(f"{API_BASE}/seniorities")
        mapping: dict[int, ExperienceLevel] = {}
        for item in data.get("data", []):
            name: str = (item.get("attributes", {}) or {}).get("name", "")
            level = SENIORITY_MAP.get(name.strip().lower())
            if level is not None:
                mapping[int(item["id"])] = level
        self._seniority_map = mapping
        return mapping

    def fetch(self) -> list[dict]:
        all_jobs: list[dict] = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            url = (
                f"{API_BASE}/search/jobs"
                f"?per_page=120&page={page}&expand[]=company"
            )
            resp = _request(url)
            company_map = _build_company_map(resp.get("included", []))

            for job in resp.get("data", []):
                company_ref = (
                    (job.get("attributes", {}) or {}).get("company", {}) or {}
                ).get("data") or {}
                company_id = str(company_ref["id"]) if company_ref.get("id") else None
                job["_company_name"] = (
                    company_map.get(company_id) if company_id else None
                )
                all_jobs.append(job)

            meta = resp.get("meta", {})
            total_pages = meta.get("total_pages", 1)
            page += 1

        return all_jobs

    def parse(self, raw: list[dict]) -> list[dict]:
        return [item for item in raw if item.get("type") == "job"]

    def normalize(self, parsed: list[dict]) -> list[JobData]:
        seniority_map = self._load_seniorities()
        result: list[JobData] = []

        for item in parsed:
            attrs = item.get("attributes", {}) or {}
            links = item.get("links", {}) or {}

            title = (attrs.get("title") or "").strip()
            if not title:
                continue

            company_name = item.get("_company_name") or "Unknown"

            published_ts = attrs.get("published_at")
            posted_at = None
            if isinstance(published_ts, (int, float)):
                posted_at = datetime.fromtimestamp(published_ts, tz=timezone.utc)

            seniority_data = (attrs.get("seniority") or {}).get("data") or {}
            seniority_id = seniority_data.get("id")
            experience_level = (
                seniority_map.get(int(seniority_id)) if seniority_id else None
            )

            raw_min = attrs.get("min_salary")
            raw_max = attrs.get("max_salary")

            salary_min = (
                Decimal(str(raw_min)).quantize(Decimal("0.01"))
                if raw_min is not None
                else None
            )
            salary_max = (
                Decimal(str(raw_max)).quantize(Decimal("0.01"))
                if raw_max is not None
                else None
            )

            countries = attrs.get("countries") or []
            remote_modality = attrs.get("remote_modality") or ""
            location_parts = [str(c) for c in countries]
            if remote_modality and remote_modality != "no_remote":
                location_parts.append(remote_modality.replace("_", " ").title())
            location = ", ".join(location_parts) if location_parts else None

            raw_url = links.get("public_url")
            source_url = str(raw_url) if raw_url else None

            description = _strip_html(attrs.get("description"))

            result.append(
                JobData(
                    title=title,
                    company_name=company_name,
                    description=description,
                    location=location,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    currency=None,
                    employment_type=None,
                    experience_level=experience_level,
                    source=Source.GETONBOARD,
                    external_id=str(item["id"]) if item.get("id") else None,
                    source_url=source_url,
                    posted_at=posted_at,
                    raw_data=item,
                )
            )

        return result


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )

    import asyncio

    from app.db.session import AsyncSessionLocal
    from app.scrapers.service import ScraperService

    scraper = GetOnBoardScraper()
    logger.info("Scraping GetOnBoard...")
    start = time.perf_counter()

    try:
        data = scraper.scrape()
    except Exception:
        logger.exception("Scraping failed")
        return

    logger.info("Found: %d", len(data))

    async def _persist() -> None:
        async with AsyncSessionLocal() as session:
            service = ScraperService(session)
            await service.persist(data)

    asyncio.run(_persist())

    elapsed = time.perf_counter() - start
    logger.info("Done in %.1f s", elapsed)


if __name__ == "__main__":
    main()
