import logging
import math
from typing import Optional
from ..models.idea import KeywordAnalysis, YouTubeAnalysis, CourseInfo
from .market_competition import YouTubeAPIScraper
from ...core.config import settings

logger = logging.getLogger(__name__)


class YouTubeService:
    """
    Service to analyze YouTube educational content for course topics.
    Searches for relevant videos and extracts insights about popularity, engagement, and content.
    """
    
    def __init__(self, max_results: int = 20):
        """Initialize YouTube service with API configuration."""
        self.max_results = max_results
        self.youtube_key = settings.YOUTUBE_API_KEY
        
        # Check if API key is configured
        logger.info(f"Initializing YouTubeService with API key: {'SET' if self.youtube_key else 'NOT SET'}")
        
        if not self.youtube_key:
            logger.warning("YouTube API key not configured. YouTube analysis will be skipped.")
            self._api_available = False
            self.scraper = None
        else:
            logger.info("YouTube API key found, enabling YouTube analysis")
            self._api_available = True
            self.scraper = YouTubeAPIScraper(api_key=self.youtube_key, max_results=self.max_results)
    
    async def analyze_youtube(self, keywords: KeywordAnalysis) -> Optional[YouTubeAnalysis]:
        """
        Perform complete YouTube analysis for a course topic.
        
        Args:
            keywords: KeywordAnalysis with topic and keywords
            
        Returns:
            YouTubeAnalysis with YouTube insights, or None if API unavailable
        """
        if not self._api_available or not self.scraper:
            logger.info("Skipping YouTube analysis - API not configured")
            return None
        
        logger.info(f"Analyzing YouTube content for topic: {keywords.topic}")
        
        try:
            # Fetch videos for the main topic
            videos = await self.scraper.fetch_courses(keywords.topic)
            
            if not videos:
                logger.info(f"No YouTube videos found for topic: {keywords.topic}")
                return YouTubeAnalysis(
                    total_videos_found=0,
                    top_videos=[],
                    avg_views=None,
                    avg_rating=None,
                    top_channels=[],
                    total_views=0,
                    engagement_score=0
                )
            
            # Calculate statistics
            total_views = sum(video.student_count or 0 for video in videos)
            avg_views = total_views / len(videos) if videos else 0
            
            # Calculate average rating
            ratings = [v.rating for v in videos if v.rating is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else None
            
            # Get top videos (sorted by views)
            top_videos = sorted(
                videos,
                key=lambda v: v.student_count or 0,
                reverse=True
            )[:10]  # Top 10 videos
            
            # Extract top channels (most popular channels)
            channel_counts = {}
            for video in videos:
                if video.instructor:
                    channel_counts[video.instructor] = channel_counts.get(video.instructor, 0) + (video.student_count or 0)
            
            top_channels = sorted(
                channel_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 channels
            top_channel_names = [channel[0] for channel in top_channels]
            
            # Calculate engagement score (0-100)
            # Based on average likes/views ratio and average views
            engagement_score = self._calculate_engagement_score(videos, avg_views)
            
            logger.info(f"YouTube analysis complete: {len(videos)} videos found, "
                       f"avg views: {avg_views:,.0f}, engagement score: {engagement_score}")
            
            return YouTubeAnalysis(
                total_videos_found=len(videos),
                top_videos=top_videos,
                avg_views=avg_views if avg_views > 0 else None,
                avg_rating=avg_rating,
                top_channels=top_channel_names,
                total_views=int(total_views),
                engagement_score=engagement_score
            )
            
        except Exception as e:
            logger.error(f"Error in YouTube analysis: {str(e)}")
            return None
    
    def _calculate_engagement_score(self, videos: list[CourseInfo], avg_views: float) -> int:
        """
        Calculate engagement score (0-100) based on video metrics.
        Represents overall demand and engagement level for the topic.
        
        Factors:
        - Average views (logarithmic scale, up to 60 points for very high-demand topics)
        - Total views (indicator of overall market size, up to 20 points)
        - Average rating (up to 20 points)
        """
        if not videos:
            return 0
        
        # Score based on average views using logarithmic scale (0-60 points)
        # This better reflects high-demand topics with millions of views
        # Scale: 10K views = 20, 100K = 40, 1M = 55, 5M+ = 60
        if avg_views > 0:
            # Use log10 scale: log10(views) gives us exponential growth representation
            log_views = math.log10(max(avg_views, 1000))  # Min 1000 to avoid log(0)
            # Map log scale to 0-60: log10(1000)=3 → 20pts, log10(1M)=6 → 55pts, log10(10M)=7 → 60pts
            views_score = min(60, max(0, (log_views - 3) * 10 + 20))
        else:
            views_score = 0
        
        # Score based on total views (market size indicator, 0-20 points)
        total_views_sum = sum(v.student_count or 0 for v in videos)
        if total_views_sum > 0:
            log_total = math.log10(max(total_views_sum, 10000))
            # Map: 10K total = 5pts, 1M = 15pts, 100M+ = 20pts
            total_views_score = min(20, max(0, (log_total - 4) * 5 + 5))
        else:
            total_views_score = 0
        
        # Score based on average rating (0-20 points)
        ratings = [v.rating for v in videos if v.rating is not None]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            # Scale: 3.0 rating = 10pts, 4.0 = 15pts, 5.0 = 20pts
            rating_score = max(0, min(20, (avg_rating - 3.0) * 10 + 10))
        else:
            rating_score = 10  # Neutral score if no ratings available
        
        # Combine scores
        total_score = views_score + total_views_score + rating_score
        
        return int(round(min(100, max(0, total_score))))


# Singleton instance
youtube_service = YouTubeService()

