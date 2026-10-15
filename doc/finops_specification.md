# FinOps Specification: Developer AI Spend Controls & Unit Economics

> **Document Version**: 1.0.0  
> **Target Audience**: FinOps Teams, Engineering Leadership, Finance Business Partners  
> **Focus**: Measuring Real Cost per Accepted Change, Wasted Spend, Context ROI, and Hard Budget Caps

---

## 1. Overview & Core Philosophy

Traditional cloud FinOps focuses on idle virtual machines, storage tiers, and reserved instances. **Developer AI FinOps** introduces a new paradigm where costs are driven by autonomous loops, token context windows, non-deterministic model completions, and failed test cycles.

A platform cannot merely measure token counts; it must answer the fundamental enterprise question:  
**"How many dollars did we spend to successfully merge an approved change into production?"**

This specification defines the metrics, math, ledger structure, and control mechanisms implemented in the ADLC FinOps platform consuming Compass, Distil, and Halos.

---

## 2. Core Unit Economic Metrics

### Metric 1: Cost per Accepted Change ($ / Merged PR)
The true cost of AI-assisted engineering includes both successful runs and the iterations that led up to them.

$$\text{Cost per Accepted Task} = \frac{\sum \text{Net Task Spend (USD)}}{\max(1, \text{Accepted Tasks})}$$

- **Target**: Continuous downward trend as prompt templates, test harnesses, and model routing mature.
- **Data Sources**: Compass review/test/fix loop spend records + GitHub/GitLab PR merge status.

### Metric 2: Wasted Spend Ratio (%)
Measures money spent on sessions that were halted by budget caps, failed test suites, or were rejected during human review.

$$\text{Wasted Spend Ratio} = \left(\frac{\sum \text{Cost of Failed or Halted Tasks}}{\sum \text{Total Net Spend}}\right) \times 100$$

- **Target**: $< 20\%$. Ratios exceeding $35\%$ trigger alerts to review repo test health or prompt ambiguity in the SDLC feedback loop.

### Metric 3: Distil Context Compression Net ROI
Compressing context tokens saves dollars, but compression computation or proxy latency introduces overhead. Furthermore, if compression degrades reasoning, the agent might require more iterations, negating the savings.

$$\text{Gross Savings} = (\text{Raw Tokens} - \text{Compressed Tokens}) \times \text{Input Token Rate (\$/token)}$$

$$\text{Net Savings} = \text{Gross Savings} - \text{Compression Service Overhead}$$

$$\text{Compression ROI Ratio} = \frac{\text{Net Savings}}{\max(\$0.01, \text{Compression Overhead})}$$

- Distil empirically audits this (`distil audit`), verifying that the agent's decision fidelity remains $\ge 97\%$ before aggressive compression is allowed.

---

## 3. Three-Tier Budget Ceiling Hierarchy

The platform enforces three distinct, non-bypassable budget tiers:

```
┌────────────────────────────────────────────────────────┐
│ Tier 1: Enterprise Monthly Budget Cap                  │
│ Enforced by: ADLC FinOps Global Controller ($50,000)   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Tier 2: Repository / Cost-Center Budget                │
│ Enforced by: Halos Gateway Quota & Route ($500 - $2,500)│
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Tier 3: Per-Session Agent Hard Cap                     │
│ Enforced by: Compass COMPASS_MAX_USD ($1.50 - $15.00)  │
└────────────────────────────────────────────────────────┘
```

1. **Enterprise Monthly Cap ($50,000 default)**:
   - Aggregated across all repositories.
   - At 80% utilization: triggers proactive warning to FinOps administrators.
   - At 100% utilization: automatically limits execution to low-risk tasks and canary rings.
2. **Repository / Cost-Center Cap**:
   - Set during Self-Service Onboarding.
   - Attributed to the declared billing owner.
3. **Session Hard Ceiling (`COMPASS_MAX_USD`)**:
   - Injected into Claude Code, Codex, or Gemini CLI by Compass.
   - Monitored on every iteration.
   - If accumulated session spend reaches the ceiling, Compass immediately halts the agent process with the message:
     > *"Budget ceiling reached: this session has spent ~$X.XX, at or over your $X.XX cap. Stopping before it spends more."*

---

## 4. Ledger Schema & Reconciliation

The platform maintains an immutable SQLite ledger (`finops_ledger`) recording each AI task execution:

```sql
CREATE TABLE finops_ledger (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    repository TEXT NOT NULL,
    developer_id TEXT NOT NULL,
    model TEXT NOT NULL,
    task_class TEXT NOT NULL,
    gross_cost_usd REAL NOT NULL,
    compression_saved_usd REAL NOT NULL,
    net_cost_usd REAL NOT NULL,
    accepted INTEGER NOT NULL,
    failure_reason TEXT
);
```

### Reconciliation with Distil Receipts & Gateway Logs
- For each completed task, `distil_receipt_id` is linked in the `evidence_records` table.
- Distil receipts prove exact token counts and cached token re-use.
- Monthly billing audits cross-reference Gateway invoices with the aggregated `net_cost_usd` ledger.

---

## 5. Emergency Signed Kill Switch

In the event of an unexpected runaway agent loop, model hallucination cascade, or cost anomaly:
1. Operator triggers Kill Switch in Dashboard or via CLI:
   ```bash
   adlc-finops finops kill-switch --activate --reason "Runaway loop detected in billing service"
   ```
2. The FinOps Service creates a cryptographically signed kill token (`ed25519:<token>`).
3. The token is broadcast to Halos, which publishes it to all connected AI gateways.
4. Gateways begin rejecting model completion requests within **10 seconds**, halting further expenditure across the entire fleet.
