"""Models for Self-Service Coding-Agent Onboarding (P0)."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from adlc_finops.models import DataClassification, EnvironmentType, RolloutRing

class OnboardingRequest(BaseModel):
    developer_id: str = Field(..., description="Developer SSO or corporate username")
    repository: str = Field(..., description="Repository full name, e.g., org/repo")
    environment_type: EnvironmentType = Field(default=EnvironmentType.LOCAL_WORKSTATION)
    data_classification: DataClassification = Field(default=DataClassification.INTERNAL)
    policy_profile_id: str = Field(default="prof-standard-dev")
    monthly_budget_cap_usd: float = Field(default=500.00, ge=10.0, le=50000.0)
    enable_distil_compression: bool = Field(default=True)
    target_ring: RolloutRing = Field(default=RolloutRing.CANARY_5)

class BoundedVerificationResult(BaseModel):
    task_id: str
    status: str
    cost_usd: float
    iterations: int
    tests_verified: bool
    human_merge_gate_verified: bool

class OnboardingResponse(BaseModel):
    onboarding_id: str
    developer_id: str
    repository: str
    status: str
    halos_token: str
    compass_session_token: str
    assigned_ring: str
    budget_cap_usd: float
    verification_evidence: BoundedVerificationResult
    onboarded_at: str
    message: str

class OnboardingRecord(BaseModel):
    id: str
    developer_id: str
    repository: str
    environment_type: str
    data_classification: str
    assigned_profile_id: str
    budget_cap_usd: float
    status: str
    created_at: str
