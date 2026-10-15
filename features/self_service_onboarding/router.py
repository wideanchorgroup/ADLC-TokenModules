"""FastAPI Router for Self-Service Coding-Agent Onboarding (P0)."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from .models import OnboardingRequest, OnboardingResponse, OnboardingRecord
from .service import OnboardingService

router = APIRouter(prefix="/api/v1/onboarding", tags=["P0 - Self-Service Onboarding"])
service = OnboardingService()

@router.post("/enroll", response_model=OnboardingResponse)
def enroll_developer_and_repo(req: OnboardingRequest):
    """Enroll a developer + repository into the governed AI platform."""
    try:
        return service.onboard_developer_repo(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[OnboardingRecord])
def get_onboarded_entities():
    """Retrieve all enrolled developer/repo entities and their assigned budgets."""
    return service.list_onboardings()
