"""FastAPI Router for Unified Task Evidence Record (P0)."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from .models import CreateEvidenceRecordRequest, EvidenceRecordDTO, EvidenceAuditFilter
from .service import UnifiedEvidenceService

router = APIRouter(prefix="/api/v1/evidence", tags=["P0 - Unified Task Evidence Record"])
service = UnifiedEvidenceService()

@router.post("/record", response_model=EvidenceRecordDTO)
def record_evidence(req: CreateEvidenceRecordRequest):
    """Store unified task evidence linking work item, git commit, agent ID, compass/distil/halos versions, test results, cost, and approvals."""
    try:
        return service.create_record(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/records", response_model=List[EvidenceRecordDTO])
def list_records(
    repository: Optional[str] = Query(None),
    developer_id: Optional[str] = Query(None),
    model_name: Optional[str] = Query(None),
    outcome: Optional[str] = Query(None)
):
    """Query evidence records for audit, cost attribution, incident investigation, and reproducibility."""
    filters = EvidenceAuditFilter(
        repository=repository,
        developer_id=developer_id,
        model_name=model_name,
        outcome=outcome
    )
    return service.query_records(filters)
