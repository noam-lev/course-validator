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
            "job_titles": ["3-5 actual job titles that require this skill"],
            "course_type": {{
                "type": "one of: professional, personal, life_skills, educational",
                "description": "explanation of why this type was chosen",
                "focus_areas": ["3-4 key areas this type of course should focus on"]
            }}
        }}
        
        Course Types Explained:
        1. life_skills: Personal finance, investing, health, relationships, self-improvement
           - Focus on practical life applications
           - Skills everyone needs regardless of profession
           - Often involves money, health, or personal growth
           
        2. professional: Career advancement, job skills, certifications
           - Direct application in workplace
           - Clear career path connection
           - Industry-specific skills
           
        3. personal: Hobby, creative pursuits, personal interests
           - Pure enjoyment or creativity
           - No specific practical application needed
           - Personal fulfillment focused
           
        4. educational: Academic subjects, teaching methods, exam prep
           - Traditional academic topics
           - Formal education focus
           - Structured learning paths
        
        Choose the most appropriate type based on:
        - Primary motivation (job vs personal growth vs hobby)
        - Target audience (professionals vs general public)
        - Expected outcomes (career advancement vs personal enrichment)
        - Application (workplace vs daily life vs leisure)
        
        Guidelines and Examples:
        
        1. Keywords (what people search to LEARN):
           - Technical: "learn python", "javascript tutorial", "data science basics"
           - Education: "fun math games for kids", "teaching reading activities", "homeschool curriculum"
           - Business: "start online business", "marketing strategy guide", "leadership skills"
           - Creative: "learn digital painting", "photography basics", "video editing tutorial"
        
        2. Job Search Terms (professional terms from job requirements):
           - Technical: "Python", "React", "machine learning", "AWS"
           - Education: "curriculum development", "instructional design", "early childhood education"
           - Business: "project management", "strategic planning", "team leadership"
           - Creative: "content creation", "visual design", "video production"
        
        3. Job Titles (actual positions that would use these skills):
           - Technical: "Software Engineer", "Data Scientist", "DevOps Engineer"
           - Education: "Educational Consultant", "Curriculum Developer", "Learning Specialist"
           - Business: "Business Coach", "Management Consultant", "Training Specialist"
           - Creative: "Content Creator", "Digital Media Specialist", "Creative Director"
        
        Match your response to the course domain (technical, educational, business, creative, etc.).
        Focus on professional, employable skills even for hobby/lifestyle topics.
        
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