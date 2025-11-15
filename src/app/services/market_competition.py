from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
import asyncio
from datetime import datetime
import logging
import re

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

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


class YouTubeAPIScraper(CourseMarketplaceScraper):
    """
    YouTube Data API v3 scraper for educational content.
    Searches for tutorials/courses and returns video information.
    Requires YOUTUBE_API_KEY environment variable.
    """

    def __init__(self, api_key: Optional[str] = None, max_results: int = 20):
        self._platform_name = "youtube"
        self.api_key = api_key or self._get_api_key_from_env()
        self.max_results = min(max_results, 50)  # YouTube API limit per request
        self.base_url = "https://www.googleapis.com/youtube/v3"

    @property
    def platform_name(self) -> str:
        return self._platform_name

    def _get_api_key_from_env(self) -> Optional[str]:
        """Try to get YouTube API key from environment."""
        from ...core.config import settings
        return settings.YOUTUBE_API_KEY

    async def fetch_courses(self, topic: str) -> List[CourseInfo]:
        """
        Fetch educational videos for a topic from YouTube using Data API v3.
        """
        if not self.api_key:
            logger.warning("YouTube API key not configured. Skipping YouTube search.")
            return []

        # Build search query to find tutorials/courses
        search_query = f"{topic} tutorial course"
        
        logger.info(f"Searching YouTube for: {search_query}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Search for videos
                params = {
                    "part": "snippet",
                    "q": search_query,
                    "type": "video",
                    "videoDuration": "long",  # Filter for substantial content (long videos are typically courses)
                    "videoDefinition": "any",
                    "maxResults": self.max_results,
                    "key": self.api_key,
                    "relevanceLanguage": "en",
                    "order": "relevance",
                }
                
                response = await client.get(f"{self.base_url}/search", params=params)
                
                if response.status_code == 403:
                    logger.error("YouTube API quota exceeded or invalid API key")
                    return []
                
                response.raise_for_status()
                data = response.json()
                
                video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
                
                if not video_ids:
                    logger.info(f"No videos found for: {search_query}")
                    return []
                
                # Get detailed video statistics
                courses = await self._fetch_video_details(client, video_ids)
                
                logger.info(f"Found {len(courses)} YouTube videos for: {topic}")
                return courses
                
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
            except:
                error_detail = f" - {e.response.text[:200] if hasattr(e.response, 'text') else 'Unable to parse error'}"
            logger.warning(f"HTTP error fetching YouTube data: {e.response.status_code}{error_detail}")
            return []
        except Exception as e:
            logger.warning(f"Error fetching YouTube data: {str(e)}")
            return []

    async def _fetch_video_details(self, client: httpx.AsyncClient, video_ids: List[str]) -> List[CourseInfo]:
        """Fetch detailed information about videos."""
        try:
            params = {
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(video_ids),
                "key": self.api_key,
            }
            
            response = await client.get(f"{self.base_url}/videos", params=params)
            response.raise_for_status()
            data = response.json()
            
            courses = []
            now = datetime.utcnow()
            
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                statistics = item.get("statistics", {})
                
                # Extract view count as a proxy for "student count"
                view_count = int(statistics.get("viewCount", 0))
                
                # Calculate a realistic rating from likes/views ratio (scaled to 5.0)
                # Typical YouTube like ratios: 0.3-2% (good videos), 2-5% (excellent)
                # Scale: 0.3% = 3.0 stars, 0.5% = 3.5 stars, 1% = 4.0 stars, 2%+ = 5.0 stars
                likes = int(statistics.get("likeCount", 0))
                rating = None
                if view_count > 0 and likes > 0:
                    like_ratio = likes / view_count
                    # Use logarithmic scale for more realistic ratings
                    # Formula: 3.0 + (like_ratio * 1000) with caps at 3.0-5.0
                    rating = min(5.0, max(3.0, 3.0 + (like_ratio * 1000)))
                
                course = CourseInfo(
                    title=snippet.get("title", "Unknown"),
                    url=f"https://www.youtube.com/watch?v={item['id']}",
                    price=0.0,  # YouTube is free
                    rating=rating,
                    student_count=view_count,
                    platform=self.platform_name,
                    instructor=snippet.get("channelTitle"),
                    last_updated=now,
                    level=None,
                )
                courses.append(course)
            
            return courses
            
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
            except:
                error_detail = f" - {e.response.text[:200] if hasattr(e.response, 'text') else 'Unable to parse error'}"
            logger.warning(f"Error fetching video details: HTTP {e.response.status_code}{error_detail}")
            return []
        except Exception as e:
            logger.warning(f"Error fetching video details: {str(e)}")
            return []


class PlaywrightUdemyScraper(CourseMarketplaceScraper):
    """
    Udemy scraper using Playwright for full browser rendering.
    Bypasses anti-bot protection by using a real Chrome browser.
    """

    def __init__(self, timeout: float = 30.0, max_courses: int = 20, headless: bool = True):
        self._platform_name = "udemy"
        self.timeout = timeout * 1000  # Playwright uses milliseconds
        self.max_courses = max_courses
        self.base_url = "https://www.udemy.com"
        self.headless = headless
        self._browser: Optional[Browser] = None
        self._playwright = None

    @property
    def platform_name(self) -> str:
        return self._platform_name

    async def _ensure_browser(self):
        """Initialize browser if not already running."""
        if self._browser is None:
            logger.info("Initializing Playwright browser...")
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=self.headless)
            logger.info("Browser initialized successfully")

    async def close(self):
        """Clean up browser resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def fetch_courses(self, topic: str) -> List[CourseInfo]:
        """
        Fetch courses for a topic from Udemy using Playwright.
        Uses topic pages (e.g., /topic/python/) which load course listings.
        """
        # Clean topic for URL (lowercase, replace spaces with hyphens)
        clean_topic = topic.lower().strip().replace(" ", "-")
        # Remove any special characters except hyphens
        clean_topic = re.sub(r"[^a-z0-9\-]", "", clean_topic)
        
        url = f"{self.base_url}/topic/{clean_topic}/"
        
        logger.info(f"Fetching Udemy courses from: {url}")
        
        try:
            await self._ensure_browser()
            
            # Create a new page
            page = await self._browser.new_page()
            
            try:
                # Navigate to the page
                logger.info("Loading page...")
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
                
                # Wait for course cards to appear
                # Try multiple selectors as Udemy's DOM structure varies
                try:
                    await page.wait_for_selector(
                        "[data-purpose='course-card-container'], .course-card-module, [class*='course-card']",
                        timeout=10000
                    )
                    logger.info("Course cards found on page")
                except PlaywrightTimeoutError:
                    logger.warning("Timeout waiting for course cards - may not have loaded")
                
                # Small wait for dynamic content
                await asyncio.sleep(1)
                
                # Get the rendered HTML
                html = await page.content()
                
                # Parse the HTML
                courses = self._parse_course_page(html, url)
                
                logger.info(f"Successfully fetched {len(courses)} courses from Udemy")
                return courses
                
            finally:
                await page.close()
                    
        except PlaywrightTimeoutError:
            logger.warning(f"Timeout loading {url}")
            return []
        except Exception as e:
            logger.warning(f"Error fetching {url}: {str(e)}")
            return []

    def _parse_course_page(self, html: str, page_url: str) -> List[CourseInfo]:
        """
        Parse Udemy HTML to extract course information.
        Looks for various course card patterns in the rendered DOM.
        """
        soup = BeautifulSoup(html, "html.parser")
        courses: List[CourseInfo] = []
        now = datetime.utcnow()
        
        # Try multiple selectors - Udemy's structure varies by region/experiment
        course_cards = []
        
        # Strategy 1: data-purpose attribute
        course_cards = soup.find_all("div", attrs={"data-purpose": "course-card-container"})
        if not course_cards:
            # Strategy 2: class-based (may contain 'course-card')
            course_cards = soup.find_all("div", class_=re.compile(r"course-card"))
        if not course_cards:
            # Strategy 3: Look for course links
            course_links = soup.find_all("a", href=re.compile(r"/course/[^/]+/"))
            # Group by parent container
            seen_parents = set()
            for link in course_links:
                parent = link.find_parent("div", class_=re.compile(r"card|course"))
                if parent and id(parent) not in seen_parents:
                    course_cards.append(parent)
                    seen_parents.add(id(parent))
        
        logger.info(f"Found {len(course_cards)} potential course cards in HTML")
        
        for card in course_cards[:self.max_courses]:
            try:
                course_info = self._extract_course_from_card(card)
                if course_info:
                    courses.append(course_info)
            except Exception as e:
                logger.debug(f"Error parsing course card: {str(e)}")
                continue
        
        logger.info(f"Successfully parsed {len(courses)} courses from Udemy")
        return courses

    def _extract_course_from_card(self, card) -> Optional[CourseInfo]:
        """Extract course information from a single course card."""
        now = datetime.utcnow()
        
        # Find title and URL
        title_link = None
        
        # Try various selectors for the course link
        title_link = card.find("a", href=re.compile(r"/course/[^/]+/"))
        if not title_link:
            title_link = card.find("a", attrs={"data-purpose": "course-title-url"})
        
        if not title_link:
            return None
        
        # Extract title (might be in nested elements)
        title = title_link.get_text(strip=True)
        if not title:
            # Try to find title in child elements
            title_elem = title_link.find(["h3", "h4", "div"], class_=re.compile(r"title|heading"))
            if title_elem:
                title = title_elem.get_text(strip=True)
        
        href = title_link.get("href", "")
        
        # Make URL absolute
        if href.startswith("/"):
            url = f"{self.base_url}{href}"
        else:
            url = href
        
        if not title or not url:
            return None
        
        # Extract price
        price = 0.0
        price_elem = card.find(["span", "div"], class_=re.compile(r"price"))
        if not price_elem:
            price_elem = card.find(["span", "div"], attrs={"data-purpose": re.compile(r"price")})
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r"[\d,]+\.?\d*", price_text.replace(",", ""))
            if price_match:
                try:
                    price = float(price_match.group())
                except ValueError:
                    pass
        
        # Extract rating
        rating = None
        rating_elem = card.find(["span", "div"], class_=re.compile(r"rating|star"))
        if not rating_elem:
            rating_elem = card.find(["span", "div"], attrs={"data-purpose": re.compile(r"rating")})
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            rating_match = re.search(r"[\d.]+", rating_text)
            if rating_match:
                try:
                    rating = float(rating_match.group())
                except ValueError:
                    pass
        
        # Extract student count
        student_count = None
        enrollment_elem = card.find(["span", "div"], string=re.compile(r"student|enroll", re.IGNORECASE))
        if enrollment_elem:
            enrollment_text = enrollment_elem.get_text(strip=True)
            enrollment_text = enrollment_text.replace(",", "")
            count_match = re.search(r"(\d+)", enrollment_text)
            if count_match:
                try:
                    student_count = int(count_match.group(1))
                except ValueError:
                    pass
        
        return CourseInfo(
            title=title,
            url=url,
            price=price,
            rating=rating,
            student_count=student_count,
            platform=self.platform_name,
            instructor=None,
            last_updated=now,
            level=None,
        )


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


# Default singleton configured with scrapers
# 
# Configuration priority:
# 1. If YOUTUBE_API_KEY is set, use YouTube Data API (real, free, reliable)
# 2. Otherwise, use MockMarketplaceScraper (fast, predictable, for development)
#
# To get a YouTube API key:
# 1. Go to https://console.cloud.google.com/
# 2. Create a project or select existing
# 3. Enable "YouTube Data API v3"
# 4. Create credentials (API key)
# 5. Set YOUTUBE_API_KEY environment variable
#
def _create_default_scrapers() -> List[CourseMarketplaceScraper]:
    """Create default scrapers based on available API keys."""
    from ...core.config import settings
    
    scrapers: List[CourseMarketplaceScraper] = []
    
    # Try YouTube API if key is available
    youtube_key = settings.YOUTUBE_API_KEY
    if youtube_key:
        logger.info("YouTube API key found - using YouTube Data API for competition analysis")
        scrapers.append(YouTubeAPIScraper(api_key=youtube_key))
    else:
        logger.info("No YouTube API key found - using mock scraper")
        scrapers.append(MockMarketplaceScraper())
    
    return scrapers

market_competition_service = MarketCompetitionService(
    scrapers=_create_default_scrapers(),
    max_concurrency=3,
)

# Alternative configurations:
#
# 1. Mock only (for testing):
# market_competition_service = MarketCompetitionService(
#     scrapers=[MockMarketplaceScraper()],
#     max_concurrency=5,
# )
#
# 2. YouTube only:
# market_competition_service = MarketCompetitionService(
#     scrapers=[YouTubeAPIScraper(api_key="your-key")],
#     max_concurrency=3,
# )
#
# 3. Multiple platforms:
# market_competition_service = MarketCompetitionService(
#     scrapers=[YouTubeAPIScraper(), MockMarketplaceScraper()],
#     max_concurrency=3,
# )

__all__ = [
    "CourseMarketplaceScraper",
    "MockMarketplaceScraper",
    "YouTubeAPIScraper",
    "PlaywrightUdemyScraper",
    "MarketCompetitionService",
    "market_competition_service",
]


