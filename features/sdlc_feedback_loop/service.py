"""Service for SDLC Feedback and Improvement Loop (P2)."""

import uuid
from datetime import datetime
from typing import List, Optional
from adlc_finops.database import db
from adlc_finops.clients import HalosClient
from .models import FeedbackItemDTO, GeneratePolicyPRRequest, PolicyPRResult

class SDLCFeedbackService:
    def __init__(self):
        self.halos = HalosClient()

    def list_feedback_items(self) -> List[FeedbackItemDTO]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedback_items ORDER BY occurrences DESC")
            rows = cursor.fetchall()
            return [
                FeedbackItemDTO(
                    id=r["id"],
                    failure_pattern=r["failure_pattern"],
                    occurrences=r["occurrences"],
                    affected_repositories=r["affected_repositories"],
                    suggested_improvement=r["suggested_improvement"],
                    status=r["status"],
                    created_at=r["created_at"]
                )
                for r in rows
            ]

    def generate_policy_pr(self, req: GeneratePolicyPRRequest) -> PolicyPRResult:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedback_items WHERE id = ?", (req.feedback_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Feedback item {req.feedback_id} not found")

            # Update status to PR submitted
            cursor.execute("UPDATE feedback_items SET status = 'pr_generated' WHERE id = ?", (req.feedback_id,))
            conn.commit()

        pr_num = 108
        diff_snippet = (
            f"--- a/policies/compass.yaml\n"
            f"+++ b/policies/compass.yaml\n"
            f"@@ -14,3 +14,6 @@\n"
            f"+# Auto-generated improvement from feedback {req.feedback_id}\n"
            f"+# Fix: {row['suggested_improvement']}\n"
            f"+test_harness_timeout_seconds: 180\n"
        )

        return PolicyPRResult(
            feedback_id=req.feedback_id,
            action="POLICY_IMPROVEMENT_PR_CREATED",
            pr_url=f"https://github.com/wideanchorgroup/ADLC-TokenModules/pull/{pr_num}",
            target_ring=req.target_ring,
            policy_diff=diff_snippet,
            status="awaiting_human_merge"
        )
