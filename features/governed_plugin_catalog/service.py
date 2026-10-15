"""Service for Governed Plugin / MCP Catalog (P1)."""

import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from adlc_finops.database import db
from adlc_finops.clients import CompassClient
from adlc_finops.models import PluginApprovalStatus
from .models import PluginRegistrationRequest, PluginStatusUpdateRequest, GovernedPluginDTO

class GovernedPluginService:
    def __init__(self):
        self.compass = CompassClient()

    def register_plugin(self, req: PluginRegistrationRequest) -> GovernedPluginDTO:
        plugin_id = f"plg-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()

        # Execute Compass plugin scan
        scan_res = self.compass.scan_plugin(
            plugin_name=req.name,
            manifest={"permissions": req.permissions, "destinations": req.data_destinations}
        )
        scan_score = scan_res.get("score", 95)
        is_safe = scan_res.get("safe", True)
        initial_status = PluginApprovalStatus.APPROVED.value if is_safe else PluginApprovalStatus.RESTRICTED.value

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO governed_plugins VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plugin_id,
                req.name,
                req.version,
                req.owner,
                json.dumps(req.permissions),
                json.dumps(req.data_destinations),
                initial_status,
                scan_score,
                now
            ))
            conn.commit()

        return GovernedPluginDTO(
            id=plugin_id,
            name=req.name,
            version=req.version,
            owner=req.owner,
            permissions=req.permissions,
            data_destinations=req.data_destinations,
            status=initial_status,
            scan_score=scan_score,
            added_at=now
        )

    def list_plugins(self) -> List[GovernedPluginDTO]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM governed_plugins ORDER BY added_at DESC")
            rows = cursor.fetchall()
            return [
                GovernedPluginDTO(
                    id=r["id"],
                    name=r["name"],
                    version=r["version"],
                    owner=r["owner"],
                    permissions=json.loads(r["permissions"]),
                    data_destinations=json.loads(r["data_destinations"]),
                    status=r["status"],
                    scan_score=r["scan_score"],
                    added_at=r["added_at"]
                )
                for r in rows
            ]

    def update_plugin_status(self, plugin_id: str, req: PluginStatusUpdateRequest) -> GovernedPluginDTO:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE governed_plugins SET status = ? WHERE id = ?
            """, (req.status.value, plugin_id))
            conn.commit()

        plugins = {p.id: p for p in self.list_plugins()}
        if plugin_id not in plugins:
            raise ValueError(f"Plugin {plugin_id} not found")
        return plugins[plugin_id]
