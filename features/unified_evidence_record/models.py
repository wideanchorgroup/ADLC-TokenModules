"""Models for Unified Task Evidence Record (P0)."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CreateEvidenceRecordRequest(BaseModel):
    work_item: str = Field(..., description="Issue tracker ID, e.g. JIRA-1234 or GH-42")
    repository: str = Field(..., description="Target repository")
    base_commit: str = Field(..., description="Base git commit SHA")
    developer_id: str = Field(..., description="Developer who initiated task")
    agent_identity: str = Field(default="claude-code-agent-01", description="CLI or agent process ID")
    compass_policy_hash: str = Field(default="cmp-pol-sha256-default")
    halos_release_id: str = Field(default="rel-2026.10.4-signed")
    model_name: str = Field(default="anthropic/claude-3-7-sonnet")
    distil_receipt_id: str = Field(default="dst-rcpt-lossless-01")
    billed_cost_usd: float = Field(..., ge=0.0)
    tokens_saved: int = Field(default=0)
    distil_savings_usd: float = Field(default=0.0)
    test_passed: bool = Field(default=True)
    pr_number: Optional[int] = Field(None)
    human_approver: Optional[str] = Field(None)
    merge_outcome: str = Field(default="merged", description="merged, rejected, halted_budget, pending_review")

class EvidenceRecordDTO(BaseModel):
    task_id: str
    work_item: str
    repository: str
    base_commit: str
    developer_id: str
    agent_identity: str
    compass_policy_hash: str
    halos_release_id: str
    model_name: str
    distil_receipt_id: str
    billed_cost_usd: float
    tokens_saved: int
    distil_savings_usd: float
    test_passed: bool
    pr_number: Optional[int]
    human_approver: Optional[str]
    merge_outcome: str
    created_at: str

class EvidenceAuditFilter(BaseModel):
    repository: Optional[str] = None
    developer_id: Optional[str] = None
    model_name: Optional[str] = None
    outcome: Optional[str] = None
