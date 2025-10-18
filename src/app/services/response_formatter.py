"""
Response formatting service to ensure consistent and clear response formatting.
"""
import logging
from typing import Optional, Dict, Any, List
from ..models.idea import JobMarketData

logger = logging.getLogger(__name__)

class ResponseFormattingError(Exception):
    """Custom exception for response formatting errors."""
    pass

class ResponseFormatter:
    @staticmethod
    def format_score(score: int) -> str:
        """
        Format a score as a percentage with explanation of the scale.
        
        Args:
            score: Integer score to format (must be between 0 and 100)
            
        Returns:
            Formatted score string
            
        Raises:
            ResponseFormattingError: If score is not between 0 and 100
        """
        try:
            if not isinstance(score, int):
                raise ResponseFormattingError(f"Score must be an integer, got {type(score)}")
            if not 0 <= score <= 100:
                raise ResponseFormattingError(f"Score must be between 0 and 100, got {score}")
            
            formatted = f"{score}% (0-100 scale)"
            logger.debug(f"Formatted score {score} to '{formatted}'")
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting score: {str(e)}")
            raise ResponseFormattingError(f"Failed to format score: {str(e)}")
    
    @staticmethod
    def format_salary(salary: float) -> str:
        """
        Format salary with currency symbol and commas.
        
        Args:
            salary: Float value representing the salary
            
        Returns:
            Formatted salary string with currency symbol and commas
            
        Raises:
            ResponseFormattingError: If salary is negative or not a number
        """
        try:
            if not isinstance(salary, (int, float)):
                raise ResponseFormattingError(f"Salary must be a number, got {type(salary)}")
            if salary < 0:
                raise ResponseFormattingError(f"Salary cannot be negative, got {salary}")
            
            formatted = f"${salary:,.2f}"
            logger.debug(f"Formatted salary {salary} to '{formatted}'")
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting salary: {str(e)}")
            raise ResponseFormattingError(f"Failed to format salary: {str(e)}")
    
    @staticmethod
    def get_score_explanation(score_type: str, score: int) -> str:
        """
        Get explanation for different types of scores.
        
        Args:
            score_type: Type of score ('demand', 'competition', or 'good_idea')
            score: Integer score to get explanation for (must be between 0 and 100)
            
        Returns:
            String explanation of the score
            
        Raises:
            ResponseFormattingError: If score_type is invalid or score is out of range
        """
        try:
            if not isinstance(score, int):
                raise ResponseFormattingError(f"Score must be an integer, got {type(score)}")
            if not 0 <= score <= 100:
                raise ResponseFormattingError(f"Score must be between 0 and 100, got {score}")
                
            valid_types = {'demand', 'competition', 'good_idea'}
            if score_type not in valid_types:
                raise ResponseFormattingError(f"Invalid score type '{score_type}'. Must be one of: {', '.join(valid_types)}")
            
            logger.debug(f"Getting explanation for {score_type} score: {score}")
            explanations = {
            "demand": {
                range(0, 30): "Very low market demand",
                range(30, 50): "Low market demand",
                range(50, 70): "Moderate market demand",
                range(70, 85): "High market demand",
                range(85, 101): "Very high market demand"
            },
            "competition": {
                range(0, 30): "Very low competition",
                range(30, 50): "Low competition",
                range(50, 70): "Moderate competition",
                range(70, 85): "High competition",
                range(85, 101): "Very high competition"
            },
            "good_idea": {
                range(0, 30): "Not recommended at this time",
                range(30, 50): "Consider with caution",
                range(50, 70): "Moderate potential",
                range(70, 85): "Good potential",
                range(85, 101): "Excellent potential"
            }
        }
        
            score_ranges = explanations.get(score_type, {})
            for score_range, explanation in score_ranges.items():
                if score in score_range:
                    logger.debug(f"Found explanation for {score_type} score {score}: '{explanation}'")
                    return explanation
                    
            error_msg = f"No explanation found for {score_type} score {score}"
            logger.warning(error_msg)
            return "Score not available"
            
        except Exception as e:
            logger.error(f"Error getting score explanation: {str(e)}")
            raise ResponseFormattingError(f"Failed to get score explanation: {str(e)}")

    @staticmethod
    def format_content_gap_hint(
        skills: list[str],
        rising_interests: list[str],
        key_areas: list[str]
    ) -> str:
        """
        Format content gap hint in a clear, structured way.
        
        Args:
            skills: List of in-demand skills from job market
            rising_interests: List of trending topics/interests
            key_areas: List of key areas to cover
            
        Returns:
            Formatted content gap hint string
            
        Raises:
            ResponseFormattingError: If any input list contains invalid items
        """
        try:                    
            logger.debug(f"Formatting content gap hint with: skills={skills}, rising_interests={rising_interests}, key_areas={key_areas}")
            
            sections = []
            
            if skills:
                sections.append(f"Most in-demand skills: {', '.join(skills)}")
            if rising_interests:
                sections.append(f"Rising interest detected in: {', '.join(rising_interests)}")
            if key_areas:
                sections.append(f"Key areas to cover: {', '.join(key_areas)}")
                
            hint = " | ".join(sections)
            if hint:
                hint += ". Consider emphasizing these aspects in your course."
                
            logger.debug(f"Formatted content gap hint: '{hint}'")
            return hint
            
        except Exception as e:
            logger.error(f"Error formatting content gap hint: {str(e)}")
            raise ResponseFormattingError(f"Failed to format content gap hint: {str(e)}")

    @staticmethod
    def format_job_market_summary(job_market: Optional[JobMarketData]) -> str:
        """
        Format job market summary with clear structure.
        
        Args:
            job_market: Optional JobMarketData object containing job market analysis
            
        Returns:
            Formatted job market summary string
            
        Raises:
            ResponseFormattingError: If job market data is invalid
        """
        try:
            logger.debug(f"Formatting job market summary for: {job_market}")
            
            if not job_market:
                logger.debug("No job market data provided")
                return "No relevant job market data available"
                
            if not isinstance(job_market, JobMarketData):
                raise ResponseFormattingError(f"Expected JobMarketData, got {type(job_market)}")
                
            if job_market.total_jobs_found == 0:
                logger.debug("Job market data shows zero jobs found")
                return "No relevant job market data available"
                
            parts = [f"Found {job_market.total_jobs_found} relevant jobs"]
            
            if job_market.avg_salary is not None:
                try:
                    salary_str = ResponseFormatter.format_salary(job_market.avg_salary)
                    parts.append(f"average salary: {salary_str}")
                except ResponseFormattingError as e:
                    logger.warning(f"Failed to format salary: {str(e)}")
                
            if job_market.growth_trend:
                valid_trends = {"growing", "stable", "declining"}
                if job_market.growth_trend not in valid_trends:
                    raise ResponseFormattingError(f"Invalid growth trend: {job_market.growth_trend}")
                 
                parts.append(f"market trend: {job_market.growth_trend}")
                
            summary = ", ".join(parts)
            logger.debug(f"Formatted job market summary: '{summary}'")
            return summary
            
        except Exception as e:
            logger.error(f"Error formatting job market summary: {str(e)}")
            raise ResponseFormattingError(f"Failed to format job market summary: {str(e)}")

    @staticmethod
    def format_response_data(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format all response data for better clarity."""
        formatter = ResponseFormatter()
        
        # Format scores with percentages and explanations
        response_data["demand_score"] = formatter.format_score(response_data["demand_score"])
        response_data["competition_score"] = formatter.format_score(response_data["competition_score"])
        response_data["good_idea_score"] = formatter.format_score(response_data["good_idea_score"])
        
        # Add score explanations
        response_data["score_explanations"] = {
            "demand": formatter.get_score_explanation("demand", int(response_data["demand_score"].split("%")[0])),
            "competition": formatter.get_score_explanation("competition", int(response_data["competition_score"].split("%")[0])),
            "good_idea": formatter.get_score_explanation("good_idea", int(response_data["good_idea_score"].split("%")[0]))
        }
        
        # Format job market data if available
        if response_data.get("job_market"):
            job_market = response_data["job_market"]
            if job_market.get("avg_salary"):
                job_market["avg_salary"] = formatter.format_salary(job_market["avg_salary"])
                
        return response_data
