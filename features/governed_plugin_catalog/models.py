"""Models for Governed Plugin / MCP Catalog (P1)."""

from typing import List, Optional
from pydantic import BaseModel, Field
from adlc_finops.models import PluginApprovalStatus

class PluginRegistrationRequest(BaseModel):
    name: str = Field(..., description="Plugin / MCP tool name")
    version: str = Field(..., description="Semver version string")
    owner: str = Field(..., description="Team or engineer accountable for plugin")
    permissions: List[str] = Field(default_factory=list, description="Requested tool permissions, e.g. git_read, fs_write")
    data_destinations: List[str] = Field(default_factory=list, description="External domains/endpoints the tool communicates with")

class PluginStatusUpdateRequest(BaseModel):
    status: PluginApprovalStatus
    reason: str

class GovernedPluginDTO(BaseModel):
    id: str
    name: str
    version: str
    owner: str
    permissions: List[str]
    data_destinations: List[str]
    status: str
    scan_score: int
    added_at: str
