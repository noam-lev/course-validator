from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
import asyncio
from datetime import datetime
import logging

from ..models.idea import CourseInfo, MarketplaceAnalysis


logger = logging.getLogger(__name__)


class MarketCompetitionError(Exception):
    """Raised when marketplace analysis cannot be completed."""
    pass


class CourseMarketplaceScraper(ABC):
    """
    Minimal async interface for a course marketplace scraper.
    Concrete implementations should be safe to call concurrently.
    """

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Human-readable, stable platform identifier, e.g. "mock", "udemy"."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_courses(self, topic: str) -> List[CourseInfo]:
        """
        Fetch a list of courses for a topic.
        Implementations should handle their own internal retries/timeouts as needed.
        """
        raise NotImplementedError


class MockMarketplaceScraper(CourseMarketplaceScraper):
    """
    Safe mock scraper for smoke tests and incremental development.
    Simulates I/O and returns deterministic data.
    """

    def __init__(self, latency_ms: int = 150):
        self._platform_name = "mock"
        self.latency_ms = latency_ms

    @property
    def platform_name(self) -> str:
        return self._platform_name

    async def fetch_courses(self, topic: str) -> List[CourseInfo]:
        # Simulate network latency
        await asyncio.sleep(self.latency_ms / 1000)

        now = datetime.utcnow()
        # Deterministic, minimal set of courses for smoke testing
        return [
            CourseInfo(
                title=f"{topic.title()} Basics",
                url=f"https://example.com/{topic}/basics",
                price=19.99,
                rating=4.5,
                student_count=1200,
                platform=self.platform_name,
                instructor="Jane Doe",
                last_updated=now,
                level="Beginner",
            ),
            CourseInfo(
                title=f"Advanced {topic.title()}",
                url=f"https://example.com/{topic}/advanced",
                price=49.0,
                rating=4.7,
                student_count=800,
                platform=self.platform_name,
                instructor="John Smith",
                last_updated=now,
                level="Advanced",
            ),
        ]


class MarketCompetitionService:
    """
    Orchestrates concurrent marketplace scraping across topics.
    Start with a mock-only configuration; add real scrapers as they are validated.
    """

    def __init__(
        self,
        scrapers: List[CourseMarketplaceScraper],
        max_concurrency: int = 5,
    ):
        if not scrapers:
            raise ValueError("At least one scraper must be provided")
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be >= 1")

        self.scrapers = scrapers
        self.max_concurrency = max_concurrency

    async def analyze_market(self, topics: List[str]) -> MarketplaceAnalysis:
        """
        Analyze market competition across configured scrapers for the provided topics.
        Returns a MarketplaceAnalysis with aggregate counts and a simple competition score.
        """
        if not topics:
            return MarketplaceAnalysis(
                marketplaces={},
                competition_score=0,
                analyzed_marketplaces=[s.platform_name for s in self.scrapers],
                summary={"total_courses": 0, "avg_courses_per_topic": 0.0, "topics_analyzed": 0},
            )

        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def run_scrape(
            scraper: CourseMarketplaceScraper, topic: str
        ) -> Tuple[str, str, List[CourseInfo]]:
            # Concurrency guard to avoid overwhelming any single runtime
            async with semaphore:
                try:
                    courses = await scraper.fetch_courses(topic)
                    return scraper.platform_name, topic, courses
                except Exception as e:
                    logger.warning(
                        f"Scrape failed for platform={scraper.platform_name}, topic={topic}: {str(e)}"
                    )
                    return scraper.platform_name, topic, []

        tasks: List[asyncio.Task] = []
        for scraper in self.scrapers:
            for topic in topics:
                tasks.append(asyncio.create_task(run_scrape(scraper, topic)))

        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Build marketplaces structure: {platform: {topic: [CourseInfo]}}
        marketplaces: Dict[str, Dict[str, List[CourseInfo]]] = {}
        for platform_name, topic, courses in results:
            if platform_name not in marketplaces:
                marketplaces[platform_name] = {}
            marketplaces[platform_name][topic] = courses

        # Compute aggregate metrics
        total_courses = sum(len(courses) for platform in marketplaces.values() for courses in platform.values())
        num_topics = len(topics)
        avg_courses_per_topic = (total_courses / num_topics) if num_topics else 0.0

        competition_score = self._compute_competition_score(avg_courses_per_topic)

        summary = {
            "total_courses": total_courses,
            "avg_courses_per_topic": avg_courses_per_topic,
            "topics_analyzed": num_topics,
        }

        return MarketplaceAnalysis(
            marketplaces=marketplaces,
            competition_score=competition_score,
            analyzed_marketplaces=[s.platform_name for s in self.scrapers],
            summary=summary,
        )

    def _compute_competition_score(self, avg_courses_per_topic: float) -> int:
        """
        Simple baseline mapping: normalize avg courses per topic into 0-100.
        Tunable as we add richer signals (price, rating, enrollments, recency).
        """
        # Heuristic: 10 courses per topic ~ 100 competition
        normalized = min(max(avg_courses_per_topic / 10.0, 0.0), 1.0)
        return int(round(normalized * 100))


# Default singleton configured with a mock scraper for incremental testing
market_competition_service = MarketCompetitionService(
    scrapers=[MockMarketplaceScraper()],
    max_concurrency=5,
)


__all__ = [
    "CourseMarketplaceScraper",
    "MockMarketplaceScraper",
    "MarketCompetitionService",
    "market_competition_service",
]


