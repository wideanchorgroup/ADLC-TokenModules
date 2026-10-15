# Feature Matrix: 10 Enterprise Platform Features

> **Specification Reference**: Derived directly from Perplexity Architecture Proposal (Pages 2–4).  
> **Directory Convention**: Every feature is implemented in its own separate directory under `features/`.

---

## 1. Feature Breakdown Matrix

| # | Priority | Feature Name | Directory Path | What the Developer / Platform Team Gets | Components Consumed |
|---|---|---|---|---|---|
| 1 | **P0** | Self-Service Coding-Agent Onboarding | [`features/self_service_onboarding/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/self_service_onboarding/) | Enrolls a developer, repository, or CI runner into an approved profile with access, budget, and readiness checks. Runs bounded verification task. | Halos enrollment/configuration; Compass setup; optional Distil integration. |
| 2 | **P0** | Enterprise Policy Profiles | [`features/enterprise_policy_profiles/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/enterprise_policy_profiles/) | Approved configurations by repository sensitivity (Public, Internal, Confidential), dev environment, and task risk. Signed with Ed25519 signatures. | Halos signed releases; Compass execution settings; Distil context policies. |
| 3 | **P0** | Repository Qualification & Readiness Assessment | [`features/repository_qualification/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/repository_qualification/) | Actionable scorecard with 6 critical blockers: test suites, ownership, branch protection, unapproved MCPs, unsupported combinations, and billing owner. | Compass checks; existing CI/security tools; organization-specific rules. |
| 4 | **P0** | Golden-Path Task Catalog | [`features/golden_path_catalog/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/golden_path_catalog/) | Repeatable workflows for bug fixes, test generation, dependency updates, documentation, and approved refactoring with risk-based operating policies. | Compass task/review loops; existing issue and PR workflows. |
| 5 | **P0** | Unified Task Evidence Record | [`features/unified_evidence_record/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/unified_evidence_record/) | One record linking work item, agent session, tool/config versions, changes, tests, cost, approvals, and merge without centralizing raw code or secrets. | Signals/artifacts from Compass, Distil, Halos, source-control, and CI. |
| 6 | **P1** | Enterprise Evaluation & Experiment Service | [`features/enterprise_eval_service/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/enterprise_eval_service/) | Compares approved tool/model/config combinations on representative internal tasks before fleet rollout (pass@k, duration, regressions, cost/task). | Halos evaluations and experiments; Distil comparisons; Compass execution. |
| 7 | **P1** | Developer AI FinOps Dashboard & Controls | [`features/finops_dashboard_controls/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/finops_dashboard_controls/) | Unit economics ($/accepted PR, wasted spend on failed loops), budget ceilings (`COMPASS_MAX_USD`), Distil receipts, and 10s emergency kill switch. | Compass spend controls; Distil receipts; gateway billing and PR merge data. |
| 8 | **P1** | Governed Plugin / MCP Catalog | [`features/governed_plugin_catalog/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/governed_plugin_catalog/) | Approved tools with owners, versions, permissions, data destinations, and retirement policies. Compass security scanner integration. | Compass plugin scanning; Halos MCP configuration/toggles; enterprise identity. |
| 9 | **P1** | Fleet Posture and Drift Dashboard | [`features/fleet_posture_drift/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/fleet_posture_drift/) | Identifies outdated clients, configuration drift, unsupported combinations, and overdue exceptions. One-click drift remediation. | Halos fleet/configuration state; Compass installation checks. |
| 10 | **P2** | SDLC Feedback and Improvement Loop | [`features/sdlc_feedback_loop/`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/features/sdlc_feedback_loop/) | Converts recurring failures and developer corrections into reviewed configuration or workflow improvements via automated Halos policy PRs. | Evidence records; internal evaluations; Halos controlled rollout. |

---

## 2. Directory Structure Verification

Every feature folder contains three standard modules adhering to enterprise clean architecture:
- `models.py`: Request, response, and database transfer schemas (Pydantic).
- `service.py`: Business logic consuming Compass, Distil, and Halos API clients.
- `router.py`: FastAPI APIRouter exposing RESTful endpoints.
- `__init__.py`: Clean module exports for library consumers.
