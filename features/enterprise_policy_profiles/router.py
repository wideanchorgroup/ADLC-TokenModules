"""FastAPI Router for Enterprise Policy Profiles (P0)."""

from typing import List
from fastapi import APIRouter, HTTPException
from .models import PolicyProfileCreate, PolicyProfileRecord, PolicyEvaluationRequest
from .service import PolicyProfileService

router = APIRouter(prefix="/api/v1/policy-profiles", tags=["P0 - Enterprise Policy Profiles"])
service = PolicyProfileService()

@router.post("/create", response_model=PolicyProfileRecord)
def create_profile(req: PolicyProfileCreate):
    """Create a new signed policy profile combining Halos rings, Compass caps, and Distil modes."""
    try:
        return service.create_profile(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[PolicyProfileRecord])
def list_profiles():
    """List all approved enterprise policy profiles."""
    return service.list_profiles()

@router.post("/match", response_model=PolicyProfileRecord)
def match_profile(req: PolicyEvaluationRequest):
    """Dynamically determine approved policy profile for given repo, environment, and task risk."""
    return service.match_policy(req)
