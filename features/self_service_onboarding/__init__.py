"""Self-Service Coding-Agent Onboarding Feature (P0)."""

from .models import OnboardingRequest, OnboardingResponse, OnboardingRecord, BoundedVerificationResult
from .service import OnboardingService
from .router import router

__all__ = ["OnboardingRequest", "OnboardingResponse", "OnboardingRecord", "BoundedVerificationResult", "OnboardingService", "router"]
