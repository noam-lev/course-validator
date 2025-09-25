from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CourseIdeaRequest(BaseModel):
    user_input: str = Field(..., description="The course idea input from the user")

class KeywordAnalysis(BaseModel):
    topic: str
    subtopics: List[str]
    keywords: List[str]

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
    udemy: dict[str, CourseInfo]
    competition_score: int = Field(..., ge=0, le=100)

class CourseIdeaResponse(BaseModel):
    idea: str
    demand_score: int = Field(..., ge=0, le=100)
    competition_score: int = Field(..., ge=0, le=100)
    good_idea_score: int = Field(..., ge=0, le=100)
    content_gap_hint: Optional[str] = None
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "idea": "Python course for data science beginners",
                "demand_score": 70,
                "competition_score": 65,
                "good_idea_score": 72,
                "content_gap_hint": "Most existing courses focus on Python basics, but few provide real-world projects for data science beginners.",
                "summary": "This course idea has strong demand and moderate competition. You can stand out by adding project-based learning.",
                "created_at": "2025-09-25T00:00:00Z"
            }
        } 