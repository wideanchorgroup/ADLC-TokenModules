"""Models for Golden-Path Task Catalog (P0)."""

from typing import List, Optional
from pydantic import BaseModel, Field
from adlc_finops.models import TaskRiskLevel, TaskStatus

class GoldenTaskTemplate(BaseModel):
    id: str
    name: str
    task_class: str
    description: str
    risk_level: str
    standard_budget_usd: float
    require_human_merge: bool
    execution_count: int = 0
    success_rate: float = 1.0

class GoldenTaskLaunchRequest(BaseModel):
    task_template_id: str = Field(..., description="ID from golden-path catalog")
    repository: str = Field(..., description="Target repository")
    developer_id: str = Field(..., description="Triggering developer")
    work_item: str = Field(..., description="JIRA issue or GitHub issue reference")
    task_prompt: str = Field(..., description="Specific goal or instruction")
    custom_budget_usd: Optional[float] = Field(None, description="Optional custom budget override capped by policy")

class GoldenTaskExecutionResult(BaseModel):
    task_id: str
    template_id: str
    task_class: str
    risk_level: str
    status: TaskStatus
    cost_spent_usd: float
    budget_cap_usd: float
    iterations: int
    tests_passed: bool
    human_merge_required: bool
    evidence_token: str
    message: str
