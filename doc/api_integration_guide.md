# API Integration Guide: Consuming Compass, Distil, and Halos

> **Document Version**: 1.0.0  
> **Audience**: Platform Integrators, Backend Engineers, DevOps Engineers

---

## 1. Introduction

This guide documents the integration contracts between the **ADLC FinOps & Governance Control Plane** and the three underlying service technologies:
1. **Compass API / CLI Integration**
2. **Distil Context & Savings Integration**
3. **Halos Control Plane & Fleet Delivery Integration**

It also provides the REST API documentation for the ADLC FinOps Control Plane itself.

---

## 2. Consumed Service Interfaces

### 2.1 Compass Integration (`CompassClient`)

Located in [`adlc_finops/clients/compass_client.py`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/adlc_finops/clients/compass_client.py).

#### Endpoints / Capabilities Consumed:
- **Configure Session**:
  - `POST /v1/session/configure`
  - Injects `COMPASS_MAX_USD`, developer ID, repo name, and allowed command whitelist into the agent's runtime environment.
  - Returns `session_token` and confirms human merge gate requirements.
- **Guardrails Validation**:
  - `POST /v1/guardrails/check`
  - Evaluates shell commands against a 100/100 scored CI corpus, preventing destructive actions (`rm -rf /`, `curl|sh`, unsafe git pushes).
- **Bounded Task Execution**:
  - `POST /v1/tasks/execute`
  - Runs the self-fixing review/test/fix loop under hard budget constraints. Halts execution if session spend reaches `COMPASS_MAX_USD`.
- **Plugin Scanner**:
  - `POST /v1/plugins/scan`
  - Vets MCP and CLI tool manifests for dangerous privileges (e.g. root exec, raw sockets, unconfined file system access).

```python
from adlc_finops.clients import CompassClient

compass = CompassClient()
res = compass.configure_session(
    repo="wideanchorgroup/payments",
    developer_id="dev_alice",
    budget_max_usd=5.00,
    allowed_commands=["pytest", "git status", "ruff check"]
)
```

---

### 2.2 Distil Integration (`DistilClient`)

Located in [`adlc_finops/clients/distil_client.py`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/adlc_finops/clients/distil_client.py).

#### Endpoints / Capabilities Consumed:
- **Context Compression**:
  - `POST /v1/context/compress`
  - Losslessly compresses the prompt context before forwarding it to the model. Returns `compressed_tokens`, `tokens_saved`, and `receipt_id`.
- **Savings Receipts (`distil savings`)**:
  - `GET /v1/savings/{repo_or_fleet_id}`
  - Retrieves empirical token and dollar savings calculated from real developer traffic, factoring in caching.
- **Compressor Audit (`distil audit`)**:
  - `POST /v1/audit`
  - Evaluates whether compression modified the agent's decision-making on sample tasks, verifying agreement and task outcome integrity.

```python
from adlc_finops.clients import DistilClient

distil = DistilClient()
receipt = distil.compress_context("large code and test context...", mode="lossless")
print(f"Saved {receipt['tokens_saved']} tokens (${receipt['gross_savings_usd']:.4f})")
```

---

### 2.3 Halos Integration (`HalosClient`)

Located in [`adlc_finops/clients/halos_client.py`](file:///Users/ramabaswa/anthropic-projects/ADLC-TokenModules/adlc_finops/clients/halos_client.py).

#### Endpoints / Capabilities Consumed:
- **Fleet Enrollment**:
  - `POST /v1/fleet/enroll`
  - Registers developer, repository, or CI runner into an assigned rollout ring (`dark_launch`, `canary_1`, `canary_5`, `stage_25`, `ga_100`).
- **Signed Release Retrieval**:
  - `GET /v1/releases/ring/{ring}`
  - Fetches Ed25519-signed tool configurations, pinned CLI versions, and approved model routes.
- **Evaluation Gating**:
  - `POST /v1/eval/gate-check`
  - Assesses pass@k benchmark criteria, test regressions, and cost deltas before allowing release promotion to subsequent rings.
- **Emergency Kill Switch**:
  - `POST /v1/kill-switch`
  - Broadcasts a signed kill list that gateway instances pick up in ~10 seconds.
- **Rollback PR Generation**:
  - Automatically creates a rollback pull request in the policy repo when production regressions are caught.

```python
from adlc_finops.clients import HalosClient
from adlc_finops.models import RolloutRing

halos = HalosClient()
rel = halos.get_latest_signed_release(RolloutRing.CANARY_5)
print(f"Latest release: {rel['release_id']} signed by {rel['signer_identity']}")
```

---

## 3. ADLC Platform REST API Reference

The ADLC Control Plane exposes all 10 features via standard REST endpoints. OpenAPI documentation and interactive testing are available at `/docs` and `/redoc`.

| Route Prefix | Feature | Key Endpoints | Description |
|---|---|---|---|
| `/api/v1/finops` | FinOps Controls (P1) | `GET /overview`<br>`GET /breakdown/repository`<br>`GET /breakdown/model`<br>`POST /budget/update`<br>`POST /kill-switch` | Central KPI aggregation, spend breakdowns, budget caps, and emergency kill switch. |
| `/api/v1/onboarding` | Self-Service Onboarding (P0) | `POST /enroll`<br>`GET /list` | Developer + repo enrollment, Halos token generation, and bounded verification task. |
| `/api/v1/policy-profiles` | Policy Profiles (P0) | `POST /create`<br>`GET /list`<br>`POST /match` | Sensitivity × Env × Risk policy engine with Ed25519 cryptographic signing. |
| `/api/v1/qualification` | Repo Qualification (P0) | `POST /assess`<br>`GET /scorecards` | 6-point repository readiness scorecard identifying blockers. |
| `/api/v1/golden-tasks` | Golden-Path Catalog (P0) | `GET /catalog`<br>`POST /launch` | Repeatable task catalog executed under Compass review/test/fix loops. |
| `/api/v1/evidence` | Unified Evidence (P0) | `POST /record`<br>`GET /records` | Tamper-evident task ledger linking commits, agents, releases, and costs. |
| `/api/v1/evaluations` | Enterprise Evals (P1) | `POST /run`<br>`GET /history` | Comparative benchmark testing of model/tool combinations. |
| `/api/v1/plugins` | Governed Plugins (P1) | `POST /register`<br>`GET /list`<br>`PUT /{id}/status` | MCP and tool security scanning, approval, and revocation. |
| `/api/v1/fleet` | Fleet Posture (P1) | `GET /summary`<br>`POST /remediate` | Client version drift detection and forced alignment with signed releases. |
| `/api/v1/feedback` | SDLC Feedback Loop (P2) | `GET /patterns`<br>`POST /generate-pr` | Failure pattern clustering and automated Halos policy PR generation. |
