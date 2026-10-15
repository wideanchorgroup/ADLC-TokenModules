"""Models for Enterprise Policy Profiles (P0)."""

from typing import List, Optional
from pydantic import BaseModel, Field
from adlc_finops.models import DataClassification, EnvironmentType, TaskRiskLevel, RolloutRing

class PolicyProfileCreate(BaseModel):
    name: str = Field(..., description="Human-readable policy name")
    repo_sensitivity: DataClassification = Field(default=DataClassification.INTERNAL)
    environment: EnvironmentType = Field(default=EnvironmentType.LOCAL_WORKSTATION)
    task_risk: TaskRiskLevel = Field(default=TaskRiskLevel.MEDIUM)
    compass_max_usd: float = Field(default=5.00, description="Session hard budget cap enforced by Compass")
    distil_compression_mode: str = Field(default="lossless", description="Distil context compression mode (lossless/aggressive)")
    halos_ring: RolloutRing = Field(default=RolloutRing.CANARY_5, description="Rollout ring target in Halos fleet")
    require_specialist_review: bool = Field(default=False, description="Require specialized human review gate before merge")
    allowed_commands: List[str] = Field(default_factory=lambda: ["pytest", "git status", "git diff", "npm test", "ruff check"])

class PolicyProfileRecord(BaseModel):
    id: str
    name: str
    repo_sensitivity: str
    environment: str
    task_risk: str
    compass_max_usd: float
    distil_compression_mode: str
    halos_ring: str
    require_specialist_review: bool
    allowed_commands: List[str]
    signature: str
    created_at: str

class PolicyEvaluationRequest(BaseModel):
    repository: str
    sensitivity: DataClassification
    environment: EnvironmentType
    task_risk: TaskRiskLevel
