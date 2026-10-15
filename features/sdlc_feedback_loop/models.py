"""Models for SDLC Feedback and Improvement Loop (P2)."""

from typing import List, Optional
from pydantic import BaseModel, Field

class FeedbackItemDTO(BaseModel):
    id: str
    failure_pattern: str
    occurrences: int
    affected_repositories: str
    suggested_improvement: str
    status: str
    created_at: str

class GeneratePolicyPRRequest(BaseModel):
    feedback_id: str
    target_ring: str = "canary_1"
    commit_message: Optional[str] = None

class PolicyPRResult(BaseModel):
    feedback_id: str
    action: str
    pr_url: str
    target_ring: str
    policy_diff: str
    status: str
