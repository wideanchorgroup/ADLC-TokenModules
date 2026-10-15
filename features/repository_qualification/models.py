"""Models for Repository Qualification & Readiness Assessment (P0)."""

from typing import List, Optional
from pydantic import BaseModel, Field

class QualificationAssessmentRequest(BaseModel):
    repository: str = Field(..., description="Repository full name, e.g., org/repo")
    owner: Optional[str] = Field(None, description="Billing or engineering owner")
    ci_provider: str = Field(default="github-actions", description="CI platform")
    check_mcp_plugins: bool = Field(default=True)
    strict_branch_protection: bool = Field(default=True)

class ReadinessCheckItem(BaseModel):
    check_name: str
    passed: bool
    details: str
    remediation_suggestion: Optional[str] = None

class QualificationScorecard(BaseModel):
    repository: str
    owner: str
    score: int = Field(..., ge=0, le=100, description="Readiness score out of 100")
    is_qualified: bool
    test_suite_status: str
    branch_protection: bool
    codeowners_present: bool
    unapproved_mcp_count: int
    billing_owner_defined: bool
    blockers: List[str]
    check_breakdown: List[ReadinessCheckItem]
    evaluated_at: str
