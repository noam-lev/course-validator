from ..models.idea import (
    CourseIdeaRequest, 
    CourseIdeaResponse, 
    KeywordAnalysis, 
    TrendsAnalysis, 
    JobMarketData,
    ScoreExplanation,
    CourseType
)
from .response_formatter import ResponseFormatter
from .score_calculator import ScoreCalculator
from .keyword_extraction import KeywordExtractionService
from .google_trends import GoogleTrendsService
from .job_market import JobMarketService
from typing import Optional
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
        trends_service: GoogleTrendsService,
        job_market_service: JobMarketService
    ):
        self.keyword_service = keyword_service
        self.trends_service = trends_service
        self.job_market_service = job_market_service
    
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
        
        # Step 3: Analyze job market demand
        job_market_data = await self._analyze_job_market(keywords)
        
        # Step 4: Analyze competition (placeholder for future marketplace analysis)
        competition_score = await self._analyze_competition(keywords)
        
        # Step 5: Calculate overall viability score
        good_idea_score = self._calculate_viability_score(
            keywords,
            trends_analysis.demand_score,
            competition_score,
            job_market_data
        )
        
        # Step 6: Generate insights and build response
        return self._build_response(
            user_input=request.user_input,
            keywords=keywords,
            trends_analysis=trends_analysis,
            job_market_data=job_market_data,
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
    
    async def _analyze_job_market(self, keywords: KeywordAnalysis) -> Optional[JobMarketData]:
        """Analyze job market demand for extracted keywords."""
        logger.info(f"Analyzing job market for topic: {keywords.topic}")
        return await self.job_market_service.analyze_job_market(keywords)
    
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
    
    def _calculate_viability_score(
        self, 
        keywords: KeywordAnalysis,
        demand_score: int, 
        competition_score: int,
        job_market_data: Optional[JobMarketData]
    ) -> int:
        """
        Calculate overall course idea viability score using the ScoreCalculator.
        
        Args:
            keywords: Extracted keywords including course type
            demand_score: Market demand score from trends (0-100)
            competition_score: Competition level score (0-100)
            job_market_data: Job market analysis data (optional)
            
        Returns:
            Viability score (0-100)
        """
        return ScoreCalculator.calculate_viability_score(
            keywords.course_type,
            demand_score,
            competition_score,
            job_market_data
        )
    
    def _build_response(
        self,
        user_input: str,
        keywords: KeywordAnalysis,
        trends_analysis: TrendsAnalysis,
        job_market_data: Optional[JobMarketData],
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
        
        # Build job market summary
        job_summary = ""
        if job_market_data and job_market_data.total_jobs_found > 0:
            job_summary = f" Jobs found: {job_market_data.total_jobs_found}"
            if job_market_data.avg_salary:
                job_summary += f", avg salary: ${job_market_data.avg_salary:,.0f}"
        
        # Build content gap hint
        content_gap_hint = self._generate_content_gap_hint(
            keywords,
            trends_analysis,
            competition_score,
            job_market_data
        )
        
        # Build summary
        summary = (
            f"Main topic: {keywords.topic}. "
            f"Subtopics: {', '.join(keywords.subtopics)}. "
            f"trend_summary:{trend_summary}, job_summary:{job_summary}"
        )
        
        # Format scores and get explanations
        formatter = ResponseFormatter()
        formatted_demand_score = formatter.format_score(trends_analysis.demand_score)
        formatted_competition_score = formatter.format_score(competition_score)
        formatted_good_idea_score = formatter.format_score(good_idea_score)
        
        # Get score explanations
        score_explanations = ScoreExplanation(
            demand=formatter.get_score_explanation("demand", trends_analysis.demand_score),
            competition=formatter.get_score_explanation("competition", competition_score),
            good_idea=formatter.get_score_explanation("good_idea", good_idea_score)
        )
        
        # Format content gap hint
        if job_market_data and job_market_data.required_skills:
            skills = job_market_data.required_skills[:3]
        else:
            skills = []
            
        rising_keywords = [
            kw for kw, data in trends_analysis.trends.items()
            if data.direction == "rising"
        ][:3]
        
        formatted_content_gap = formatter.format_content_gap_hint(
            skills=skills,
            rising_interests=rising_keywords,
            key_areas=keywords.keywords[:3]
        )
        
        # Get score context based on course type
        score_context = ScoreCalculator.get_score_context(keywords.course_type)
        
        # Add score context to summary
        summary = f"{summary}\nScore Context: {score_context}"
        
        return CourseIdeaResponse(
            idea=user_input,
            course_type=keywords.course_type,
            demand_score=formatted_demand_score,
            competition_score=formatted_competition_score,
            good_idea_score=formatted_good_idea_score,
            score_explanations=score_explanations,
            content_gap_hint=formatted_content_gap,
            summary=summary,
            job_market=job_market_data
        )
    
    def _generate_content_gap_hint(
        self,
        keywords: KeywordAnalysis,
        trends_analysis: TrendsAnalysis,
        competition_score: int,
        job_market_data: Optional[JobMarketData]
    ) -> str:
        """
        Generate comprehensive hints about content opportunities by combining:
        - Job market required skills
        - Rising trend keywords
        - Core topic keywords
        """
        hints = []
        
        # Add job market insights if available
        if job_market_data and job_market_data.required_skills:
            top_skills = job_market_data.required_skills[:3]
            hints.append(
                f"Most in-demand skills from job market: {', '.join(top_skills)}"
            )
        
        # Add rising trend insights
        rising_keywords = [
            kw for kw, data in trends_analysis.trends.items()
            if data.direction == "rising"
        ]
        if rising_keywords:
            hints.append(
                f"Rising interest detected in: {', '.join(rising_keywords[:3])}"
            )
        
        # Always add core topic keywords
        hints.append(f"Key areas to cover: {', '.join(keywords.keywords[:3])}")
        
        # Combine all insights
        return " | ".join(hints) + ". Consider emphasizing these aspects in your course."


def get_course_analyzer() -> CourseAnalyzer:
    """
    Dependency injection factory for CourseAnalyzer.
    Used with FastAPI's Depends().
    """
    from .keyword_extraction import keyword_service
    from .google_trends import trends_service
    from .job_market import job_market_service
    
    return CourseAnalyzer(
        keyword_service=keyword_service,
        trends_service=trends_service,
        job_market_service=job_market_service
    )

