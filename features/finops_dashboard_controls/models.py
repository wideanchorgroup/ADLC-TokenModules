"""Models for Developer AI FinOps Dashboard & Controls (P1)."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FinOpsOverview(BaseModel):
    total_spend_usd: float
    accepted_tasks: int
    failed_tasks: int
    total_tasks: int
    cost_per_accepted_task: float
    total_wasted_spend_usd: float
    wasted_spend_ratio_pct: float
    distil_gross_savings_usd: float
    distil_net_savings_usd: float
    compression_roi_ratio: float
    monthly_budget_cap_usd: float
    budget_utilization_pct: float
    kill_switch_active: bool
    currency: str = "USD"

class SpendBreakdownItem(BaseModel):
    category: str
    total_spend_usd: float
    accepted_count: int
    failed_count: int
    wasted_spend_usd: float
    avg_task_cost_usd: float

class UpdateBudgetCapRequest(BaseModel):
    scope: str = Field(default="global", description="global or repository name")
    new_budget_cap_usd: float = Field(..., gt=0.0)
    alert_threshold_pct: float = Field(default=80.0, ge=50.0, le=100.0)

class KillSwitchControlRequest(BaseModel):
    activate: bool = Field(..., description="True to halt LLM traffic, False to resume")
    reason: str = Field(..., description="Operational reason for kill switch change")
    affected_models: Optional[List[str]] = Field(default=None)

class KillSwitchStatus(BaseModel):
    active: bool
    reason: str
    propagation_time_sec: float
    gateways_notified: int
    signed_token: str
    updated_at: str
