"""FastAPI Router for Governed Plugin / MCP Catalog (P1)."""

from typing import List
from fastapi import APIRouter, HTTPException
from .models import PluginRegistrationRequest, PluginStatusUpdateRequest, GovernedPluginDTO
from .service import GovernedPluginService

router = APIRouter(prefix="/api/v1/plugins", tags=["P1 - Governed Plugin/MCP Catalog"])
service = GovernedPluginService()

@router.post("/register", response_model=GovernedPluginDTO)
def register_plugin(req: PluginRegistrationRequest):
    """Register and scan a new tool/MCP plugin with Compass security analysis."""
    try:
        return service.register_plugin(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[GovernedPluginDTO])
def list_governed_plugins():
    """List approved, restricted, and revoked plugins with ownership and data egress info."""
    return service.list_plugins()

@router.put("/{plugin_id}/status", response_model=GovernedPluginDTO)
def update_plugin_status(plugin_id: str, req: PluginStatusUpdateRequest):
    """Approve, restrict, or revoke an MCP plugin across the enterprise fleet."""
    try:
        return service.update_plugin_status(plugin_id, req)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
