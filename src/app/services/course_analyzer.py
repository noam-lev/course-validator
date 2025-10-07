from ..models.idea import CourseIdeaRequest, CourseIdeaResponse, KeywordAnalysis, TrendsAnalysis
from .keyword_extraction import KeywordExtractionService
from .google_trends import GoogleTrendsService
import logging

logger = logging.getLogger(__name__)


class CourseAnalyzer:
    """
    Orchestrates the full course idea analysis workflow.
    Coordinates keyword extraction, trends analysis, marketplace analysis, and scoring.
    """
    
    def __init__(
        self,
        keyword_service: KeywordExtractionService,
        trends_service: GoogleTrendsService
    ):
        self.keyword_service = keyword_service
        self.trends_service = trends_service
    
    async def analyze_course_idea(self, request: CourseIdeaRequest) -> CourseIdeaResponse:
        """
        Perform complete analysis of a course idea.
        
        Args:
            request: CourseIdeaRequest with user input
            
        Returns:
            CourseIdeaResponse with all analysis results
        """
        # Step 1: Extract keywords using OpenAI
        keywords = await self._extract_keywords(request.user_input)
        
        # Step 2: Analyze market demand using Google Trends
        trends_analysis = await self._analyze_trends(keywords)
        
        # Step 3: Analyze competition (placeholder for future marketplace analysis)
        competition_score = await self._analyze_competition(keywords)
        
        # Step 4: Calculate overall viability score
        good_idea_score = self._calculate_viability_score(
            trends_analysis.demand_score,
            competition_score
        )
        
        # Step 5: Generate insights and build response
        return self._build_response(
            user_input=request.user_input,
            keywords=keywords,
            trends_analysis=trends_analysis,
            competition_score=competition_score,
            good_idea_score=good_idea_score
        )
    
    async def _extract_keywords(self, user_input: str) -> KeywordAnalysis:
        """Extract keywords and topics from user input."""
        logger.info("Extracting keywords from user input")
        return await self.keyword_service.extract_keywords(user_input)
    
    async def _analyze_trends(self, keywords: KeywordAnalysis) -> TrendsAnalysis:
        """Analyze Google Trends data for extracted keywords."""
        logger.info(f"Analyzing trends for topic: {keywords.topic}")
        return await self.trends_service.analyze_trends(keywords)
    
    async def _analyze_competition(self, keywords: KeywordAnalysis) -> int:
        """
        Analyze marketplace competition.
        TODO: Implement marketplace analysis service
        
        Returns:
            Competition score (0-100)
        """
        # Placeholder until marketplace analysis is implemented
        logger.info("Using placeholder competition score")
        return 65
    
    def _calculate_viability_score(self, demand_score: int, competition_score: int) -> int:
        """
        Calculate overall course idea viability score.
        
        Args:
            demand_score: Market demand score (0-100)
            competition_score: Competition level score (0-100, higher = more competition)
            
        Returns:
            Viability score (0-100)
            
        Formula:
            - 60% weight on demand (higher is better)
            - 40% weight on competition gap (lower competition is better)
        """
        # Lower competition is better, so invert it
        competition_gap = 100 - competition_score
        
        viability = int(
            (demand_score * 0.6) + 
            (competition_gap * 0.4)
        )
        
        return max(0, min(100, viability))
    
    def _build_response(
        self,
        user_input: str,
        keywords: KeywordAnalysis,
        trends_analysis: TrendsAnalysis,
        competition_score: int,
        good_idea_score: int
    ) -> CourseIdeaResponse:
        """Build the final response with all analysis results."""
        
        # Get trend information for the main topic
        main_topic_trend = trends_analysis.trends.get(
            keywords.topic,
            list(trends_analysis.trends.values())[0] if trends_analysis.trends else None
        )
        
        # Build trend summary
        trend_summary = ""
        if main_topic_trend:
            trend_summary = f" Market trend: {main_topic_trend.direction} (interest score: {main_topic_trend.score})"
        
        # Build content gap hint
        content_gap_hint = self._generate_content_gap_hint(
            keywords,
            trends_analysis,
            competition_score
        )
        
        # Build summary
        summary = (
            f"Main topic: {keywords.topic}. "
            f"Subtopics: {', '.join(keywords.subtopics)}."
            f"{trend_summary}"
        )
        
        return CourseIdeaResponse(
            idea=user_input,
            demand_score=trends_analysis.demand_score,
            competition_score=competition_score,
            good_idea_score=good_idea_score,
            content_gap_hint=content_gap_hint,
            summary=summary
        )
    
    def _generate_content_gap_hint(
        self,
        keywords: KeywordAnalysis,
        trends_analysis: TrendsAnalysis,
        competition_score: int
    ) -> str:
        """Generate a helpful hint about potential content gaps."""
        
        # Find rising trend keywords
        rising_keywords = [
            kw for kw, data in trends_analysis.trends.items()
            if data.direction == "rising"
        ]
        
        if rising_keywords:
            return (
                f"Rising interest detected in: {', '.join(rising_keywords[:3])}. "
                f"Consider focusing on these trending aspects."
            )
        
        # Default hint based on extracted keywords
        return f"Key areas to cover: {', '.join(keywords.keywords[:5])}"


def get_course_analyzer() -> CourseAnalyzer:
    """
    Dependency injection factory for CourseAnalyzer.
    Used with FastAPI's Depends().
    """
    from .keyword_extraction import keyword_service
    from .google_trends import trends_service
    
    return CourseAnalyzer(
        keyword_service=keyword_service,
        trends_service=trends_service
    )

