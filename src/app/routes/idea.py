from fastapi import APIRouter, HTTPException
from ..models.idea import CourseIdeaRequest, CourseIdeaResponse
from ..services.keyword_extraction import keyword_service

router = APIRouter(prefix="/api/ideas", tags=["ideas"])

@router.post("/analyze", response_model=CourseIdeaResponse)
async def analyze_course_idea(request: CourseIdeaRequest) -> CourseIdeaResponse:
    """
    Analyze a course idea and return insights about demand, competition, and viability.
    """
    try:
        # Extract keywords using OpenAI
        keywords = await keyword_service.extract_keywords(request.user_input)
        
        # Temporary mock scores until we implement other services
        return CourseIdeaResponse(
            idea=request.user_input,
            demand_score=70,  # Will come from trends analysis
            competition_score=65,  # Will come from marketplace analysis
            good_idea_score=72,  # Will be calculated from all scores
            content_gap_hint=f"Keywords extracted: {', '.join(keywords.keywords)}",
            summary=f"Main topic: {keywords.topic}. Subtopics: {', '.join(keywords.subtopics)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 