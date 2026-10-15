"""Service for Fleet Posture & Drift Dashboard (P1)."""

from datetime import datetime, timezone
from typing import List, Optional
from adlc_finops.database import db
from adlc_finops.clients import HalosClient, CompassClient
from .models import FleetNodeDTO, FleetPostureSummary, RemediateDriftRequest

class FleetPostureService:
    def __init__(self):
        self.halos = HalosClient()
        self.compass = CompassClient()

    def get_summary(self) -> FleetPostureSummary:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fleet_nodes ORDER BY drift_detected DESC, node_id ASC")
            rows = cursor.fetchall()

            nodes: List[FleetNodeDTO] = []
            drifted_cnt = 0
            outdated_cnt = 0
            healthy_cnt = 0

            for r in rows:
                drift = bool(r["drift_detected"])
                if drift:
                    drifted_cnt += 1
                    remediation = f"Run 'halo pull --ring {r['ring']}' to align CLI and local policies"
                else:
                    healthy_cnt += 1
                    remediation = "In sync with signed ring release"

                nodes.append(FleetNodeDTO(
                    node_id=r["node_id"],
                    developer_id=r["developer_id"],
                    cli_name=r["cli_name"],
                    installed_version=r["installed_version"],
                    pinned_version=r["pinned_version"],
                    ring=r["ring"],
                    drift_detected=drift,
                    last_heartbeat=r["last_heartbeat"],
                    status=r["status"],
                    remediation=remediation
                ))

            total = len(nodes)
            compliance = round((healthy_cnt / max(1, total)) * 100.0, 1)

            return FleetPostureSummary(
                total_nodes=total,
                healthy_nodes=healthy_cnt,
                drifted_nodes=drifted_cnt,
                outdated_nodes=outdated_cnt,
                compliance_rate_pct=compliance,
                nodes=nodes
            )

    def remediate_node(self, req: RemediateDriftRequest) -> FleetNodeDTO:
        now = datetime.now(timezone.utc).isoformat()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pinned_version FROM fleet_nodes WHERE node_id = ?", (req.node_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Node {req.node_id} not found in fleet")
            pinned = row["pinned_version"]

            cursor.execute("""
                UPDATE fleet_nodes
                SET installed_version = ?, drift_detected = 0, status = 'healthy', last_heartbeat = ?
                WHERE node_id = ?
            """, (pinned, now, req.node_id))
            conn.commit()

        summary = self.get_summary()
        matched = [n for n in summary.nodes if n.node_id == req.node_id]
        return matched[0]
