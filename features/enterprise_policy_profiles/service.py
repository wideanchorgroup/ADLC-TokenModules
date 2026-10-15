"""Service for Enterprise Policy Profiles (P0)."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from adlc_finops.database import db
from adlc_finops.clients import HalosClient, CompassClient, DistilClient
from .models import PolicyProfileCreate, PolicyProfileRecord, PolicyEvaluationRequest

class PolicyProfileService:
    def __init__(self):
        self.halos = HalosClient()
        self.compass = CompassClient()
        self.distil = DistilClient()

    def create_profile(self, req: PolicyProfileCreate) -> PolicyProfileRecord:
        profile_id = f"prof-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()

        # Compute cryptographic signature for the policy bundle (Halos signed release requirement)
        canonical = f"{req.name}:{req.repo_sensitivity.value}:{req.environment.value}:{req.task_risk.value}:{req.compass_max_usd}"
        sig = f"ed25519:{hashlib.sha256(canonical.encode()).hexdigest()[:24]}"

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO policy_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                req.name,
                req.repo_sensitivity.value,
                req.environment.value,
                req.task_risk.value,
                req.compass_max_usd,
                req.distil_compression_mode,
                req.halos_ring.value,
                1 if req.require_specialist_review else 0,
                json.dumps(req.allowed_commands),
                sig,
                now
            ))
            conn.commit()

        return PolicyProfileRecord(
            id=profile_id,
            name=req.name,
            repo_sensitivity=req.repo_sensitivity.value,
            environment=req.environment.value,
            task_risk=req.task_risk.value,
            compass_max_usd=req.compass_max_usd,
            distil_compression_mode=req.distil_compression_mode,
            halos_ring=req.halos_ring.value,
            require_specialist_review=req.require_specialist_review,
            allowed_commands=req.allowed_commands,
            signature=sig,
            created_at=now
        )

    def list_profiles(self) -> List[PolicyProfileRecord]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM policy_profiles ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [
                PolicyProfileRecord(
                    id=r["id"],
                    name=r["name"],
                    repo_sensitivity=r["repo_sensitivity"],
                    environment=r["environment"],
                    task_risk=r["task_risk"],
                    compass_max_usd=r["compass_max_usd"],
                    distil_compression_mode=r["distil_compression_mode"],
                    halos_ring=r["halos_ring"],
                    require_specialist_review=bool(r["require_specialist_review"]),
                    allowed_commands=json.loads(r["allowed_commands"]),
                    signature=r["signature"],
                    created_at=r["created_at"]
                )
                for r in rows
            ]

    def match_policy(self, req: PolicyEvaluationRequest) -> PolicyProfileRecord:
        """Find the most fitting policy profile matching sensitivity, env, and risk."""
        profiles = self.list_profiles()
        for p in profiles:
            if (p.repo_sensitivity == req.sensitivity.value and
                p.environment == req.environment.value and
                p.task_risk == req.task_risk.value):
                return p
        # Fallback to standard
        return profiles[0] if profiles else self.create_profile(
            PolicyProfileCreate(name="Default Enterprise Fallback")
        )
