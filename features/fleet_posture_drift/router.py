"""FastAPI Router for Fleet Posture & Drift Dashboard (P1)."""

from fastapi import APIRouter, HTTPException
from .models import FleetPostureSummary, RemediateDriftRequest, FleetNodeDTO
from .service import FleetPostureService

router = APIRouter(prefix="/api/v1/fleet", tags=["P1 - Fleet Posture & Drift"])
service = FleetPostureService()

@router.get("/summary", response_model=FleetPostureSummary)
def get_fleet_summary():
    """Retrieve fleet health, client version drift, and ring alignment."""
    return service.get_summary()

@router.post("/remediate", response_model=FleetNodeDTO)
def remediate_drift(req: RemediateDriftRequest):
    """Enforce signed release alignment on drifted developer node."""
    try:
        return service.remediate_node(req)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
