from abc import ABC, abstractmethod

from app.models.job import Source
from app.scrapers.schemas import JobData


class BaseScraper(ABC):
    source: Source

    @abstractmethod
    def fetch(self) -> list[dict]:
        ...

    @abstractmethod
    def parse(self, raw: list[dict]) -> list[dict]:
        ...

    @abstractmethod
    def normalize(self, parsed: list[dict]) -> list[JobData]:
        ...

    def scrape(self) -> list[JobData]:
        raw = self.fetch()
        parsed = self.parse(raw)
        return self.normalize(parsed)
