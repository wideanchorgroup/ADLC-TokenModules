"""Models for Enterprise Evaluation and Experiment Service (P1)."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RunExperimentRequest(BaseModel):
    experiment_name: str = Field(..., description="Name of experiment, e.g. Claude 3.7 vs Gemini 2.5 Flash")
    candidate_model: str = Field(..., description="Model ID to evaluate")
    tool_combination: str = Field(default="Compass+Distil(lossless)", description="Stack config")
    sample_size: int = Field(default=10, ge=1, le=100, description="Number of representative internal tasks")
    max_budget_cap_usd: float = Field(default=25.0, description="Total budget ceiling for evaluation run")
    target_rollout_ring: str = Field(default="canary_1")

class EvaluationVerdictDTO(BaseModel):
    id: str
    experiment_name: str
    tool_combination: str
    model_candidate: str
    pass_at_k: float = Field(..., description="Pass@k rate on representative tasks")
    cost_per_accepted_task: float
    avg_completion_time_sec: float
    security_regressions: int
    verdict: str
    recommendation: str
    created_at: str
