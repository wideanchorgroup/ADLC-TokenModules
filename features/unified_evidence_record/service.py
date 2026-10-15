"""Service for Unified Task Evidence Record (P0)."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from adlc_finops.database import db
from .models import CreateEvidenceRecordRequest, EvidenceRecordDTO, EvidenceAuditFilter

class UnifiedEvidenceService:
    def create_record(self, req: CreateEvidenceRecordRequest) -> EvidenceRecordDTO:
        task_id = f"task-ev-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evidence_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                req.work_item,
                req.repository,
                req.base_commit,
                req.developer_id,
                req.agent_identity,
                req.compass_policy_hash,
                req.halos_release_id,
                req.model_name,
                req.distil_receipt_id,
                req.billed_cost_usd,
                req.tokens_saved,
                req.distil_savings_usd,
                1 if req.test_passed else 0,
                req.pr_number,
                req.human_approver,
                req.merge_outcome,
                now
            ))
            conn.commit()

        return EvidenceRecordDTO(
            task_id=task_id,
            work_item=req.work_item,
            repository=req.repository,
            base_commit=req.base_commit,
            developer_id=req.developer_id,
            agent_identity=req.agent_identity,
            compass_policy_hash=req.compass_policy_hash,
            halos_release_id=req.halos_release_id,
            model_name=req.model_name,
            distil_receipt_id=req.distil_receipt_id,
            billed_cost_usd=req.billed_cost_usd,
            tokens_saved=req.tokens_saved,
            distil_savings_usd=req.distil_savings_usd,
            test_passed=req.test_passed,
            pr_number=req.pr_number,
            human_approver=req.human_approver,
            merge_outcome=req.merge_outcome,
            created_at=now
        )

    def query_records(self, filters: Optional[EvidenceAuditFilter] = None) -> List[EvidenceRecordDTO]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM evidence_records WHERE 1=1"
            params = []

            if filters:
                if filters.repository:
                    query += " AND repository = ?"
                    params.append(filters.repository)
                if filters.developer_id:
                    query += " AND developer_id = ?"
                    params.append(filters.developer_id)
                if filters.model_name:
                    query += " AND model_name = ?"
                    params.append(filters.model_name)
                if filters.outcome:
                    query += " AND merge_outcome = ?"
                    params.append(filters.outcome)

            query += " ORDER BY created_at DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                EvidenceRecordDTO(
                    task_id=r["task_id"],
                    work_item=r["work_item"],
                    repository=r["repository"],
                    base_commit=r["base_commit"],
                    developer_id=r["developer_id"],
                    agent_identity=r["agent_identity"],
                    compass_policy_hash=r["compass_policy_hash"],
                    halos_release_id=r["halos_release_id"],
                    model_name=r["model_name"],
                    distil_receipt_id=r["distil_receipt_id"],
                    billed_cost_usd=r["billed_cost_usd"],
                    tokens_saved=r["tokens_saved"],
                    distil_savings_usd=r["distil_savings_usd"],
                    test_passed=bool(r["test_passed"]),
                    pr_number=r["pr_number"],
                    human_approver=r["human_approver"],
                    merge_outcome=r["merge_outcome"],
                    created_at=r["created_at"]
                )
                for r in rows
            ]
