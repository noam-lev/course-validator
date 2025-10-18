from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CourseIdeaRequest(BaseModel):
    user_input: str = Field(..., description="The course idea input from the user")

class CourseType(BaseModel):
    type: str = Field(..., pattern="^(professional|personal|life_skills|educational)$")
    description: str
    focus_areas: List[str]

class KeywordAnalysis(BaseModel):
    topic: str
    subtopics: List[str]
    keywords: List[str]
    job_search_terms: List[str]
    job_titles: List[str]
    course_type: CourseType

class TrendData(BaseModel):
    score: int = Field(..., ge=0, le=100)
    direction: str = Field(..., pattern="^(rising|steady|falling)$")

class TrendsAnalysis(BaseModel):
    trends: dict[str, TrendData]
    demand_score: int = Field(..., ge=0, le=100)

class CourseInfo(BaseModel):
    courses_found: int
    avg_price: float
    avg_rating: float
    levels: List[str]

class MarketplaceAnalysis(BaseModel):
    marketplaces: dict[str, dict[str, CourseInfo]]  # {marketplace_name: {keyword: CourseInfo}}
    competition_score: int = Field(..., ge=0, le=100)
    analyzed_marketplaces: List[str]  # List of marketplaces that were analyzed

class JobMarketData(BaseModel):
    total_jobs_found: int
    job_demand_score: int = Field(..., ge=0, le=100)
    avg_salary: Optional[float] = None
    top_job_titles: List[str]
    required_skills: List[str]
    growth_trend: str = Field(..., pattern="^(growing|stable|declining)$")

class ScoreExplanation(BaseModel):
    demand: str
    competition: str
    good_idea: str

class CourseIdeaResponse(BaseModel):
    idea: str
    course_type: CourseType
    demand_score: str
    competition_score: str
    good_idea_score: str
    score_explanations: ScoreExplanation
    content_gap_hint: Optional[str] = None
    summary: str
    job_market: Optional[JobMarketData] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "idea": "Python course for data science beginners",
                "demand_score": "70% (0-100 scale)",
                "competition_score": "65% (0-100 scale)",
                "good_idea_score": "72% (0-100 scale)",
                "score_explanations": {
                    "demand": "High market demand",
                    "competition": "Moderate competition",
                    "good_idea": "Good potential"
                },
                "content_gap_hint": "Most in-demand skills: Python, SQL, pandas | Rising interest detected in: Data Science, Machine Learning | Key areas to cover: data analysis, visualization, statistics. Consider emphasizing these aspects in your course.",
                "summary": "Main topic: Python for Data Science. Subtopics: Data Analysis, Machine Learning, Statistics. trend_summary: Market trend: rising (interest score: 81), job_summary: Jobs found: 150, avg salary: $95,000",
                "created_at": "2025-09-25T00:00:00Z"
            }
        } 