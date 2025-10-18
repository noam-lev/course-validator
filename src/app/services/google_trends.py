from pytrends.request import TrendReq
import pandas as pd
import time
import warnings
from ..models.idea import KeywordAnalysis, TrendsAnalysis, TrendData
import logging

logger = logging.getLogger(__name__)

# Suppress FutureWarning from pytrends library (pandas deprecation in fillna)
warnings.filterwarnings('ignore', category=FutureWarning, module='pytrends')


class GoogleTrendsService:
    def __init__(self, max_retries: int = 3):
        """Initialize Google Trends service with retry configuration."""
        self.max_retries = max_retries
        self.retry_delay = 2  # seconds between retries
        # Create a single pytrends instance to reuse across requests
        self.pytrends = TrendReq(
            hl='en-US',
            tz=0,
            timeout=(10, 25)  # Keep it simple, let our own retry logic handle retries
        )
    
    async def analyze_trends(self, keywords_analysis: KeywordAnalysis) -> TrendsAnalysis:
        """
        Analyze Google Trends data for extracted keywords.
        
        Args:
            keywords_analysis: KeywordAnalysis containing topic and keywords
            
        Returns:
            TrendsAnalysis with per-keyword trend data and overall demand score
        """
        # Combine topic with keywords for comprehensive analysis
        all_search_terms = [keywords_analysis.topic] + keywords_analysis.keywords
        
        # Limit to 5 keywords max to avoid API limitations
        search_terms = all_search_terms[:5]
        
        trends_data = {}
        successful_queries = []
        
        # Query trends for each keyword individually to avoid comparison issues
        for term in search_terms:
            try:
                trend_info = await self._get_keyword_trend(term)
                if trend_info:
                    trends_data[term] = trend_info
                    successful_queries.append(term)
                    # Longer delay to avoid rate limiting
                    time.sleep(1.0)  # Increased from 0.5s to 1s
            except Exception as e:
                logger.warning(f"Failed to get trend data for '{term}': {str(e)}")
                continue
        
        # Calculate overall demand score from all successful queries
        demand_score = self._calculate_demand_score(trends_data)
        
        # If no data was retrieved, return neutral values
        if not trends_data:
            logger.warning("No trend data retrieved, returning neutral scores")
            trends_data = {
                keywords_analysis.topic: TrendData(score=50, direction="steady")
            }
            demand_score = 50
        
        return TrendsAnalysis(
            trends=trends_data,
            demand_score=demand_score
        )
    
    async def _get_keyword_trend(self, keyword: str) -> TrendData | None:
        """
        Get trend data for a single keyword with retry logic.
        
        Args:
            keyword: Search term to analyze
            
        Returns:
            TrendData with score and direction, or None if failed
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Use existing pytrends instance
                self.pytrends.build_payload(
                    kw_list=[keyword],
                    cat=0,
                    timeframe='today 12-m',
                    geo='',  # Worldwide
                    gprop=''
                )
                
                # Get interest over time
                interest_df = self.pytrends.interest_over_time()
                
                if interest_df.empty or keyword not in interest_df.columns:
                    logger.warning(f"No data available for keyword: {keyword}")
                    return None
                
                # Calculate trend metrics
                return self._analyze_trend_direction(interest_df[keyword])
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed for '{keyword}': {last_error}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                    
        logger.error(f"All retries failed for '{keyword}': {last_error}")
        return None
    
    def _analyze_trend_direction(self, interest_series: pd.Series) -> TrendData:
        """
        Analyze trend direction and calculate score from interest data.
        
        Args:
            interest_series: Pandas series of interest scores over time
            
        Returns:
            TrendData with score and direction
        """
        if len(interest_series) < 4:
            # Not enough data points
            return TrendData(score=50, direction="steady")
        
        # Split into recent (last 3 months) and older (previous 9 months)
        # Assuming weekly data, ~52 weeks in 12 months
        total_points = len(interest_series)
        recent_cutoff = total_points - (total_points // 4)  # Last ~25% for recent 3 months
        
        recent_data = interest_series.iloc[recent_cutoff:]
        older_data = interest_series.iloc[:recent_cutoff]
        
        # Calculate averages
        recent_avg = recent_data.mean()
        older_avg = older_data.mean() if len(older_data) > 0 else recent_avg
        
        # Determine trend direction
        if older_avg > 0:
            change_percent = ((recent_avg - older_avg) / older_avg) * 100
        else:
            change_percent = 0
        
        if change_percent > 10:
            direction = "rising"
            trend_bonus = 10
        elif change_percent < -10:
            direction = "falling"
            trend_bonus = -10
        else:
            direction = "steady"
            trend_bonus = 0
        
        # Calculate base score (weighted average: 50% recent, 50% older)
        base_score = (recent_avg * 0.5 + older_avg * 0.5)
        
        # Apply trend bonus and cap between 0-100
        final_score = max(0, min(100, int(base_score + trend_bonus)))
        
        return TrendData(score=final_score, direction=direction)
    
    def _calculate_demand_score(self, trends_data: dict[str, TrendData]) -> int:
        """
        Calculate overall demand score from all keyword trends.
        
        Args:
            trends_data: Dictionary of keyword to TrendData
            
        Returns:
            Overall demand score (0-100)
        """
        if not trends_data:
            return 50
        
        # Calculate weighted average of all keyword scores
        total_score = sum(data.score for data in trends_data.values())
        avg_score = total_score / len(trends_data)
        
        # Apply bonus if majority of keywords are rising
        rising_count = sum(1 for data in trends_data.values() if data.direction == "rising")
        falling_count = sum(1 for data in trends_data.values() if data.direction == "falling")
        
        momentum_bonus = 0
        if rising_count > len(trends_data) / 2:
            momentum_bonus = 5  # Bonus for rising trend momentum
        elif falling_count > len(trends_data) / 2:
            momentum_bonus = -5  # Penalty for falling trend momentum
        
        # Final score with momentum bonus, capped at 0-100
        final_score = max(0, min(100, int(avg_score + momentum_bonus)))
        
        return final_score


# Create singleton instance
trends_service = GoogleTrendsService()

