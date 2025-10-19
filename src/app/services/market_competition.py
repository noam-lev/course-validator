from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page
import asyncio
from datetime import datetime
import logging
from ..models.idea import CourseInfo, MarketplaceAnalysis

logger = logging.getLogger(__name__)

class BaseCourseScraperError(Exception):
    """Base exception for course scraper errors"""
    pass

class RateLimitError(BaseCourseScraperError):
    """Raised when rate limit is hit"""
    pass

class ScraperInitError(BaseCourseScraperError):
    """Raised when scraper fails to initialize"""
    pass

class BaseCourseScraper(ABC):
    """
    Abstract base class for course marketplace scrapers.
    Provides common functionality for scraping course data from different platforms.
    """
    def __init__(self, 
                 platform_name: str,
                 request_delay: float = 2.0,
                 max_retries: int = 3,
                 retry_delay: float = 5.0):
        self.platform_name = platform_name
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._browser: Optional[Browser] = None
        self._last_request_time: Optional[float] = None

    async def __aenter__(self):
        """Set up browser when entering context"""
        try:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=True)
            return self
        except Exception as e:
            raise ScraperInitError(f"Failed to initialize browser: {str(e)}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up browser when exiting context"""
        if self._browser:
            await self._browser.close()

    @abstractmethod
    def format_search_url(self, topic: str) -> str:
        """Format the search URL for a given topic"""
        pass

    @abstractmethod
    async def extract_course_info(self, page: Page) -> List[CourseInfo]:
        """Extract course information from a search results page"""
        pass

    async def _wait_for_rate_limit(self):
        """Implement basic rate limiting"""
        if self._last_request_time is not None:
            elapsed = asyncio.get_event_loop().time() - self._last_request_time
            if elapsed < self.request_delay:
                await asyncio.sleep(self.request_delay - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def get_courses_for_topic(self, topic: str) -> List[CourseInfo]:
        """
        Get course information for a given topic.
        Implements retry logic and rate limiting.
        """
        if not self._browser:
            raise ScraperInitError("Browser not initialized. Use context manager.")

        url = self.format_search_url(topic)
        for attempt in range(self.max_retries):
            try:
                await self._wait_for_rate_limit()
                
                page = await self._browser.new_page()
                try:
                    await page.goto(url)
                    courses = await self.extract_course_info(page)
                    return courses
                finally:
                    await page.close()
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise BaseCourseScraperError(f"Failed to scrape {url} after {self.max_retries} attempts: {str(e)}")

    async def analyze_market(self, topics: List[str]) -> MarketplaceAnalysis:
        """
        Analyze market competition for given topics.
        Returns MarketplaceAnalysis with course data and competition metrics.
        """
        all_courses: Dict[str, List[CourseInfo]] = {}
        
        for topic in topics:
            try:
                courses = await self.get_courses_for_topic(topic)
                all_courses[topic] = courses
                logger.info(f"Found {len(courses)} courses for topic: {topic}")
            except BaseCourseScraperError as e:
                logger.error(f"Failed to get courses for topic {topic}: {str(e)}")
                all_courses[topic] = []

        # Calculate basic competition metrics
        total_courses = sum(len(courses) for courses in all_courses.values())
        avg_courses_per_topic = total_courses / len(topics) if topics else 0
        
        # Simple competition score calculation
        # Can be made more sophisticated based on price, ratings, etc.
        competition_score = min(int((avg_courses_per_topic / 10) * 100), 100)

        summary = {
            "total_courses": total_courses,
            "avg_courses_per_topic": avg_courses_per_topic,
            "topics_analyzed": len(topics)
        }

        return MarketplaceAnalysis(
            marketplaces={self.platform_name: all_courses},
            competition_score=competition_score,
            analyzed_marketplaces=[self.platform_name],
            summary=summary
        )
