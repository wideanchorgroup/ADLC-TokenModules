"""FastAPI Router for Enterprise Evaluation and Experiment Service (P1)."""

from typing import List
from fastapi import APIRouter, HTTPException
from .models import RunExperimentRequest, EvaluationVerdictDTO
from .service import EnterpriseEvalService

router = APIRouter(prefix="/api/v1/evaluations", tags=["P1 - Enterprise Evaluation Service"])
service = EnterpriseEvalService()

@router.post("/run", response_model=EvaluationVerdictDTO)
def run_evaluation_benchmark(req: RunExperimentRequest):
    """Run comparative benchmark on representative tasks before promoting tool/model configurations."""
    try:
        return service.run_experiment(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[EvaluationVerdictDTO])
def get_evaluation_history():
    """Retrieve history of all enterprise model/tool experiments."""
    return service.list_evaluations()
