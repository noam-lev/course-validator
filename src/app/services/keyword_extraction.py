from openai import AsyncOpenAI
import json
from ..models.idea import KeywordAnalysis
from pydantic import ValidationError
from ...core.config import settings


class KeywordExtractionService:
    def __init__(self, max_retries: int = 3):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment or .env file")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.max_retries = max_retries
        
    async def extract_keywords(self, user_input: str) -> KeywordAnalysis:
        """Extract main topic, subtopics, and keywords from user input using OpenAI."""
        
        prompt = f"""Analyze this course idea and extract key information:
        Course Idea: {user_input}
        
        Return only a JSON object with this exact structure:
        {{
            "topic": "main topic",
            "subtopics": ["2-3 relevant subtopics"],
            "keywords": ["5-7 search-optimized keywords for Google Trends/SEO"],
            "job_search_terms": ["3-5 terms that appear in job descriptions for this skill"],
            "job_titles": ["3-5 actual job titles that require this skill"]
        }}
        
        Guidelines:
        - keywords: What people search to LEARN this topic (e.g., "learn python", "python tutorial")
        - job_search_terms: Technical terms/skills from job requirements (e.g., "Python", "React", "SQL")
        - job_titles: Actual job positions that require this skill (e.g., "Data Analyst", "Frontend Developer")
        
        IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_DEFAULT_MODEL,  # Use the model from settings
                    response_format={ "type": "json_object" },
                    messages=[
                        {"role": "system", "content": "You are a course topic analyzer. Return only valid JSON with no additional text."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                result = response.choices[0].message.content
                
                # Try to parse and validate the JSON
                try:
                    # First ensure it's valid JSON
                    parsed_json = json.loads(result)
                    # Then validate against our model
                    return KeywordAnalysis.model_validate(parsed_json)
                except (json.JSONDecodeError, ValidationError) as e:
                    last_error = f"Invalid JSON format on attempt {attempt + 1}: {str(e)}"
                    continue  # Try again
                    
            except Exception as e:
                last_error = f"OpenAI API error on attempt {attempt + 1}: {str(e)}"
                continue  # Try again
                
        # If we get here, all retries failed
        raise Exception(f"Failed to extract keywords after {self.max_retries} attempts. Last error: {last_error}")

# Create a singleton instance
keyword_service = KeywordExtractionService()