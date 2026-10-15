"""FastAPI Router for Golden-Path Task Catalog (P0)."""

from typing import List
from fastapi import APIRouter, HTTPException
from .models import GoldenTaskTemplate, GoldenTaskLaunchRequest, GoldenTaskExecutionResult
from .service import GoldenPathService

router = APIRouter(prefix="/api/v1/golden-tasks", tags=["P0 - Golden-Path Task Catalog"])
service = GoldenPathService()

@router.get("/catalog", response_model=List[GoldenTaskTemplate])
def get_task_catalog():
    """Retrieve all approved repeatable golden-path task templates."""
    return service.list_templates()

@router.post("/launch", response_model=GoldenTaskExecutionResult)
def launch_golden_task(req: GoldenTaskLaunchRequest):
    """Launch a governed task under Compass review/test/fix loops with risk-based operating policies."""
    try:
        return service.launch_task(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
