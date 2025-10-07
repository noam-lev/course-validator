from fastapi import APIRouter, Depends, HTTPException
from ..models.idea import CourseIdeaRequest, CourseIdeaResponse
from ..services.course_analyzer import CourseAnalyzer, get_course_analyzer

router = APIRouter(prefix="/api/ideas", tags=["ideas"])

@router.post("/analyze", response_model=CourseIdeaResponse)
async def analyze_course_idea(
    request: CourseIdeaRequest,
    analyzer: CourseAnalyzer = Depends(get_course_analyzer)
) -> CourseIdeaResponse:
    """
    Analyze a course idea and return insights about demand, competition, and viability.
    """
    try:
        return await analyzer.analyze_course_idea(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 