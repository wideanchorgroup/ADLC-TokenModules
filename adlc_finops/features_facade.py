"""Facade providing high-level programmatic access to all 10 features for CLI and consumers."""

from typing import List, Dict, Any, Optional
from features.finops_dashboard_controls.service import FinOpsDashboardService
from features.finops_dashboard_controls.models import UpdateBudgetCapRequest, KillSwitchControlRequest
from features.self_service_onboarding.service import OnboardingService
from features.self_service_onboarding.models import OnboardingRequest
from features.repository_qualification.service import RepositoryQualificationService
from features.repository_qualification.models import QualificationAssessmentRequest
from features.golden_path_catalog.service import GoldenPathService
from features.golden_path_catalog.models import GoldenTaskLaunchRequest
from features.enterprise_policy_profiles.service import PolicyProfileService
from features.unified_evidence_record.service import UnifiedEvidenceService
from features.enterprise_eval_service.service import EnterpriseEvalService
from features.enterprise_eval_service.models import RunExperimentRequest
from features.governed_plugin_catalog.service import GovernedPluginService
from features.fleet_posture_drift.service import FleetPostureService
from features.sdlc_feedback_loop.service import SDLCFeedbackService
from adlc_finops.models import RolloutRing

_finops = FinOpsDashboardService()
_onboarding = OnboardingService()
_qualification = RepositoryQualificationService()
_golden = GoldenPathService()
_policy = PolicyProfileService()
_evidence = UnifiedEvidenceService()
_evals = EnterpriseEvalService()
_plugins = GovernedPluginService()
_fleet = FleetPostureService()
_feedback = SDLCFeedbackService()

def get_finops_overview():
    return _finops.get_overview()

def update_budget_cap(scope: str, new_cap_usd: float, threshold: float = 80.0):
    return _finops.update_budget_cap(UpdateBudgetCapRequest(scope=scope, new_budget_cap_usd=new_cap_usd, alert_threshold_pct=threshold))

def toggle_kill_switch(activate: bool, reason: str):
    return _finops.set_kill_switch(KillSwitchControlRequest(activate=activate, reason=reason))

def onboard_entity(dev_id: str, repo: str, budget_usd: float = 500.0, ring: str = "canary_5"):
    ring_enum = RolloutRing(ring) if ring in [r.value for r in RolloutRing] else RolloutRing.CANARY_5
    return _onboarding.onboard_developer_repo(OnboardingRequest(
        developer_id=dev_id,
        repository=repo,
        monthly_budget_cap_usd=budget_usd,
        target_ring=ring_enum
    ))

def assess_repository(repo: str, owner: str):
    return _qualification.assess_repository(QualificationAssessmentRequest(repository=repo, owner=owner))

def launch_golden_task(template_id: str, repo: str, prompt: str, work_item: str = "TASK-01"):
    return _golden.launch_task(GoldenTaskLaunchRequest(
        task_template_id=template_id,
        repository=repo,
        developer_id="cli-user",
        work_item=work_item,
        task_prompt=prompt
    ))

def get_fleet_summary():
    return _fleet.get_summary()

def list_governed_plugins():
    return _plugins.list_plugins()

def run_eval_experiment(name: str, model: str, stack: str = "Compass+Distil"):
    return _evals.run_experiment(RunExperimentRequest(
        experiment_name=name,
        candidate_model=model,
        tool_combination=stack
    ))
