"""Models for Fleet Posture & Drift Dashboard (P1)."""

from typing import List, Optional
from pydantic import BaseModel, Field

class FleetNodeDTO(BaseModel):
    node_id: str
    developer_id: str
    cli_name: str
    installed_version: str
    pinned_version: str
    ring: str
    drift_detected: bool
    last_heartbeat: str
    status: str
    remediation: Optional[str] = None

class FleetPostureSummary(BaseModel):
    total_nodes: int
    healthy_nodes: int
    drifted_nodes: int
    outdated_nodes: int
    compliance_rate_pct: float
    nodes: List[FleetNodeDTO]

class RemediateDriftRequest(BaseModel):
    node_id: str
    force_update_to_pinned: bool = True
