"""FastAPI Router for SDLC Feedback and Improvement Loop (P2)."""

from typing import List
from fastapi import APIRouter, HTTPException
from .models import FeedbackItemDTO, GeneratePolicyPRRequest, PolicyPRResult
from .service import SDLCFeedbackService

router = APIRouter(prefix="/api/v1/feedback", tags=["P2 - SDLC Feedback & Improvement Loop"])
service = SDLCFeedbackService()

@router.get("/patterns", response_model=List[FeedbackItemDTO])
def get_failure_patterns():
    """Retrieve clustered recurring failure patterns and suggested workflow/config improvements."""
    return service.list_feedback_items()

@router.post("/generate-pr", response_model=PolicyPRResult)
def create_improvement_pr(req: GeneratePolicyPRRequest):
    """Convert recurring developer correction into a reviewed Halos policy improvement PR."""
    try:
        return service.generate_policy_pr(req)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
