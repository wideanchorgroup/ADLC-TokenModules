"""Core models, enums, and data definitions for ADLC FinOps."""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class EnvironmentType(str, Enum):
    LOCAL_WORKSTATION = "local_workstation"
    DEV_CONTAINER = "dev_container"
    CI_RUNNER = "ci_runner"
    MANAGED_VM = "managed_vm"

class TaskRiskLevel(str, Enum):
    LOW = "low"            # Docs, formatting, typo fix
    MEDIUM = "medium"      # Standard bug fix, test addition, unit refactoring
    HIGH = "high"          # Dependencies, migration, api contracts
    CRITICAL = "critical"  # Auth, cryptography, db schema, infrastructure

class RolloutRing(str, Enum):
    HOLD = "hold"
    DARK_LAUNCH = "dark_launch"
    CANARY_1 = "canary_1"
    CANARY_5 = "canary_5"
    STAGE_25 = "stage_25"
    GENERAL_AVAILABILITY = "ga_100"

class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    HALTED_BUDGET = "halted_budget"
    BLOCKED_POLICY = "blocked_policy"
    ROLLED_BACK = "rolled_back"

class PluginApprovalStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    RESTRICTED = "restricted"
    REVOKED = "revoked"

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DRIFT_DETECTED = "drift_detected"
    OUTDATED = "outdated"
    VIOLATION = "violation"

class FinOpsMetricSummary(BaseModel):
    total_spend_usd: float
    total_tasks_run: int
    accepted_tasks: int
    failed_tasks: int
    avg_cost_per_accepted_task: float
    total_wasted_spend_usd: float
    distil_gross_savings_usd: float
    compression_roi_ratio: float
    active_agent_count: int
    budget_cap_usd: float
    budget_utilization_pct: float
    currency: str = "USD"
