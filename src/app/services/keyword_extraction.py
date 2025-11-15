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
        
        1. life_skills: Practical skills for daily life and personal well-being
           - Personal finance, investing for beginners, budgeting, saving
           - Health, fitness, nutrition, mental wellness
           - Relationships, communication, parenting
           - Self-improvement, time management, productivity
           - Key indicator: "Is this something EVERYONE needs in their personal life?"
           - Examples: "Investing for beginners", "How to budget", "Meal planning", "Stress management"
           - NOT professional if: It's about managing YOUR OWN money/health/life (not doing it as a job)
           
        2. professional: Skills for career advancement and workplace application
           - Job-specific skills, certifications, technical training
           - Industry tools, software, methodologies
           - Management, leadership, business strategy (for work)
           - Key indicator: "Is this primarily for advancing a CAREER or doing a JOB?"
           - Examples: "Python for data science", "Project management certification", "Sales training"
           - Professional if: It's about doing this AS A JOB or FOR WORK
           
        3. personal: Hobbies, creative pursuits, pure enjoyment
           - Arts, crafts, music, games
           - Pure entertainment or creative expression
           - No practical necessity
           - Key indicator: "Is this purely for fun/creativity with no practical need?"
           - Examples: "Learn to paint", "Guitar for beginners", "Chess strategies"
           
        4. educational: Academic subjects, teaching, formal learning
           - School subjects, exam preparation
           - Teaching methods, curriculum design
           - Formal education pathways
           - Key indicator: "Is this about academic learning or teaching others?"
           - Examples: "SAT prep", "Teaching math to kids", "History course"
        
        CRITICAL DISTINCTION - life_skills vs professional:
        - "Investing for beginners" → life_skills (managing YOUR money)
        - "Financial advisor certification" → professional (doing it AS A JOB)
        - "Personal finance basics" → life_skills (everyone needs this)
        - "Corporate finance analysis" → professional (workplace skill)
        - "How to budget" → life_skills (personal life skill)
        - "Budget management for managers" → professional (workplace skill)
        
        Choose the most appropriate type based on:
        - PRIMARY USE CASE: Personal life vs workplace vs hobby vs academic
        - TARGET AUDIENCE: General public vs professionals vs students
        - MAIN GOAL: Personal enrichment vs career advancement vs enjoyment vs education
        
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