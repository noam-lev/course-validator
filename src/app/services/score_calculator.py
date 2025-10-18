"""
Service for calculating scores based on course type and various metrics.
"""
from typing import Optional
from ..models.idea import JobMarketData, CourseType

class ScoreCalculator:
    @staticmethod
    def get_weights(course_type: CourseType):
        """Get scoring weights based on course type."""
        type_weights = {
            "professional": {
                "trend": 0.4,
                "job": 0.3,
                "competition": 0.3
            },
            "personal": {
                "trend": 0.7,
                "job": 0.0,
                "competition": 0.3
            },
            "life_skills": {
                "trend": 0.6,
                "job": 0.1,
                "competition": 0.3
            },
            "educational": {
                "trend": 0.5,
                "job": 0.2,
                "competition": 0.3
            }
        }
        return type_weights.get(course_type.type, type_weights["personal"])

    @staticmethod
    def calculate_viability_score(
        course_type: CourseType,
        demand_score: int,
        competition_score: int,
        job_market_data: Optional[JobMarketData]
    ) -> int:
        """
        Calculate overall viability score based on course type and metrics.
        
        Args:
            course_type: Type of course (professional, personal, etc.)
            demand_score: Market demand score from trends (0-100)
            competition_score: Competition level score (0-100)
            job_market_data: Optional job market analysis data
            
        Returns:
            Viability score (0-100)
        """
        weights = ScoreCalculator.get_weights(course_type)
        
        # For personal/hobby courses, high trend interest is MORE important
        if course_type.type in ["personal", "life_skills"]:
            # Boost demand score if trends show high interest
            if demand_score > 70:
                demand_score = min(90, demand_score + 15)
        
        # Get job market score if available and relevant
        job_score = (
            job_market_data.job_demand_score 
            if job_market_data and weights["job"] > 0 
            else 0
        )
        
        # Invert competition score (lower competition is better)
        competition_gap = 100 - competition_score
        
        # Calculate weighted score
        weighted_score = (
            (demand_score * weights["trend"]) +
            (job_score * weights["job"]) +
            (competition_gap * weights["competition"])
        )
        
        return max(0, min(100, int(weighted_score)))

    @staticmethod
    def get_score_context(course_type: CourseType) -> str:
        """Get context about how the score was calculated based on course type."""
        contexts = {
            "professional": (
                "Score heavily considers both market trends and job market demand, "
                "as this is a professionally-focused course."
            ),
            "personal": (
                "Score primarily based on market trends and competition, "
                "as this is a personal interest course where job market is less relevant."
            ),
            "life_skills": (
                "Score emphasizes market trends with some consideration of professional applications, "
                "as this is a life skills course with both personal and professional value."
            ),
            "educational": (
                "Score balances educational trends with some job market consideration, "
                "focusing on learning outcomes and market demand."
            )
        }
        return contexts.get(course_type.type, "Score based on general market trends and competition.")
