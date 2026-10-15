"""FastAPI Router for Repository Qualification & Readiness Assessment (P0)."""

from typing import List
from fastapi import APIRouter, HTTPException
from .models import QualificationAssessmentRequest, QualificationScorecard
from .service import RepositoryQualificationService

router = APIRouter(prefix="/api/v1/qualification", tags=["P0 - Repository Qualification"])
service = RepositoryQualificationService()

@router.post("/assess", response_model=QualificationScorecard)
def assess_repository(req: QualificationAssessmentRequest):
    """Run full qualification scorecard on a repository."""
    try:
        return service.assess_repository(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scorecards", response_model=List[QualificationScorecard])
def get_all_scorecards():
    """Retrieve qualification scorecards for all registered repositories."""
    return service.list_scorecards()
