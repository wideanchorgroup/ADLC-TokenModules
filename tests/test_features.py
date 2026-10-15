"""Tests for all 10 platform features."""

import pytest
from features.self_service_onboarding.service import OnboardingService
from features.self_service_onboarding.models import OnboardingRequest
from features.enterprise_policy_profiles.service import PolicyProfileService
from features.enterprise_policy_profiles.models import PolicyProfileCreate, PolicyEvaluationRequest
from features.repository_qualification.service import RepositoryQualificationService
from features.repository_qualification.models import QualificationAssessmentRequest
from features.golden_path_catalog.service import GoldenPathService
from features.golden_path_catalog.models import GoldenTaskLaunchRequest
from features.unified_evidence_record.service import UnifiedEvidenceService
from features.unified_evidence_record.models import CreateEvidenceRecordRequest
from features.enterprise_eval_service.service import EnterpriseEvalService
from features.enterprise_eval_service.models import RunExperimentRequest
from features.finops_dashboard_controls.service import FinOpsDashboardService
from features.finops_dashboard_controls.models import UpdateBudgetCapRequest, KillSwitchControlRequest
from features.governed_plugin_catalog.service import GovernedPluginService
from features.governed_plugin_catalog.models import PluginRegistrationRequest, PluginApprovalStatus, PluginStatusUpdateRequest
from features.fleet_posture_drift.service import FleetPostureService
from features.fleet_posture_drift.models import RemediateDriftRequest
from features.sdlc_feedback_loop.service import SDLCFeedbackService
from features.sdlc_feedback_loop.models import GeneratePolicyPRRequest
from adlc_finops.models import DataClassification, EnvironmentType, TaskRiskLevel, RolloutRing

# 1. Onboarding Test
def test_onboarding_service():
    svc = OnboardingService()
    req = OnboardingRequest(
        developer_id="dev_test_user",
        repository="org/test-repo",
        environment_type=EnvironmentType.LOCAL_WORKSTATION,
        monthly_budget_cap_usd=600.0,
        target_ring=RolloutRing.CANARY_5
    )
    res = svc.onboard_developer_repo(req)
    assert res.status == "active"
    assert res.budget_cap_usd == 600.0
    assert res.verification_evidence.tests_verified is True

# 2. Policy Profiles Test
def test_policy_profile_service():
    svc = PolicyProfileService()
    profile = svc.create_profile(PolicyProfileCreate(
        name="Test Policy Profile",
        repo_sensitivity=DataClassification.CONFIDENTIAL,
        environment=EnvironmentType.DEV_CONTAINER,
        task_risk=TaskRiskLevel.HIGH,
        compass_max_usd=10.0
    ))
    assert profile.compass_max_usd == 10.0
    assert profile.signature.startswith("ed25519:")

# 3. Repository Qualification Test
def test_repository_qualification_service():
    svc = RepositoryQualificationService()
    card_pass = svc.assess_repository(QualificationAssessmentRequest(repository="org/clean-service", owner="core-eng"))
    assert card_pass.is_qualified is True
    assert card_pass.score >= 80

    card_fail = svc.assess_repository(QualificationAssessmentRequest(repository="org/legacy-app", owner=""))
    assert card_fail.is_qualified is False
    assert len(card_fail.blockers) > 0

# 4. Golden Path Tasks Test
def test_golden_path_service():
    svc = GoldenPathService()
    templates = svc.list_templates()
    assert len(templates) > 0

    run_res = svc.launch_task(GoldenTaskLaunchRequest(
        task_template_id=templates[0].id,
        repository="org/clean-service",
        developer_id="dev_tester",
        work_item="TEST-101",
        task_prompt="Run golden-path verification"
    ))
    assert run_res.status.value in ["passed", "halted_budget"]
    assert run_res.cost_spent_usd > 0

# 5. Unified Evidence Test
def test_unified_evidence_service():
    svc = UnifiedEvidenceService()
    rec = svc.create_record(CreateEvidenceRecordRequest(
        work_item="JIRA-9999",
        repository="org/clean-service",
        base_commit="abc1234",
        developer_id="dev_tester",
        billed_cost_usd=3.40,
        test_passed=True
    ))
    assert rec.work_item == "JIRA-9999"
    records = svc.query_records()
    assert any(r.work_item == "JIRA-9999" for r in records)

# 6. Enterprise Evaluations Test
def test_enterprise_eval_service():
    svc = EnterpriseEvalService()
    ev = svc.run_experiment(RunExperimentRequest(
        experiment_name="Unit Test Experiment",
        candidate_model="anthropic/claude-3-7-sonnet"
    ))
    assert ev.pass_at_k > 0.8
    assert ev.security_regressions == 0

# 7. FinOps Controls Test
def test_finops_controls_service():
    svc = FinOpsDashboardService()
    ov = svc.get_overview()
    assert ov.total_tasks > 0
    assert ov.cost_per_accepted_task >= 0

    cap_res = svc.update_budget_cap(UpdateBudgetCapRequest(new_budget_cap_usd=60000.0))
    assert cap_res["new_budget_cap_usd"] == 60000.0

    ks = svc.set_kill_switch(KillSwitchControlRequest(activate=False, reason="Testing normal state"))
    assert ks.active is False

# 8. Governed Plugins Test
def test_governed_plugin_service():
    svc = GovernedPluginService()
    plg = svc.register_plugin(PluginRegistrationRequest(
        name="Unit Test Plugin",
        version="1.0.0",
        owner="security-team",
        permissions=["git_read"],
        data_destinations=["github.com"]
    ))
    assert plg.status == "approved"
    assert plg.scan_score > 80

    updated = svc.update_plugin_status(plg.id, PluginStatusUpdateRequest(
        status=PluginApprovalStatus.REVOKED,
        reason="Testing revoke"
    ))
    assert updated.status == "revoked"

# 9. Fleet Posture Test
def test_fleet_posture_service():
    svc = FleetPostureService()
    summary = svc.get_summary()
    assert summary.total_nodes > 0

# 10. SDLC Feedback Test
def test_sdlc_feedback_service():
    svc = SDLCFeedbackService()
    items = svc.list_feedback_items()
    assert len(items) > 0
    pr_res = svc.generate_policy_pr(GeneratePolicyPRRequest(feedback_id=items[0].id))
    assert "PR" in pr_res.action
