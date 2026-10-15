"""FastAPI Router for Developer AI FinOps Dashboard & Controls (P1)."""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from .models import FinOpsOverview, SpendBreakdownItem, UpdateBudgetCapRequest, KillSwitchControlRequest, KillSwitchStatus
from .service import FinOpsDashboardService

router = APIRouter(prefix="/api/v1/finops", tags=["P1 - Developer AI FinOps Controls"])
service = FinOpsDashboardService()

@router.get("/overview", response_model=FinOpsOverview)
def get_finops_overview():
    """Retrieve overarching FinOps metrics: cost per accepted change, wasted spend, Distil compression ROI, and budget caps."""
    return service.get_overview()

@router.get("/breakdown/repository", response_model=List[SpendBreakdownItem])
def get_spend_by_repository():
    """Spend breakdown grouped by repository."""
    return service.get_spend_by_repository()

@router.get("/breakdown/model", response_model=List[SpendBreakdownItem])
def get_spend_by_model():
    """Spend breakdown grouped by foundation model / provider."""
    return service.get_spend_by_model()

@router.post("/budget/update")
def update_budget_cap(req: UpdateBudgetCapRequest):
    """Dynamically set enterprise or per-repository budget ceilings enforced across Compass and Halos."""
    return service.update_budget_cap(req)

@router.post("/kill-switch", response_model=KillSwitchStatus)
def toggle_kill_switch(req: KillSwitchControlRequest):
    """Emergency halt / resume switch broadcasting signed kill list to gateways and Compass sessions."""
    return service.set_kill_switch(req)
