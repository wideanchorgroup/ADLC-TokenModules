/**
 * ADLC FinOps & Governance Control Plane - Interactive Application Script
 * Communicates with FastAPI backends for all 10 features
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initModals();
    initForms();
    loadAllData();
});

// Tab Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const panels = document.querySelectorAll('.tab-panel');
    const titleElem = document.getElementById('current-view-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.getAttribute('data-tab');
            navItems.forEach(n => n.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            item.classList.add('active');
            const targetPanel = document.getElementById(tabId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }

            const label = item.querySelector('.nav-label');
            if (label && titleElem) {
                titleElem.textContent = label.textContent;
            }
        });
    });

    // Refresh button
    const btnRefresh = document.getElementById('btn-refresh');
    if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
            btnRefresh.classList.add('rotating');
            loadAllData().finally(() => {
                setTimeout(() => btnRefresh.classList.remove('rotating'), 500);
            });
        });
    }

    // Quick kill button
    const btnQuickKill = document.getElementById('btn-quick-kill');
    if (btnQuickKill) {
        btnQuickKill.addEventListener('click', () => {
            openModal('modal-kill');
        });
    }
}

// Modal Handlers
function initModals() {
    const closeButtons = document.querySelectorAll('.modal-close, [data-close]');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-close');
            closeModal(targetId);
        });
    });

    document.getElementById('btn-open-budget-modal')?.addEventListener('click', () => openModal('modal-budget'));
    document.getElementById('btn-run-assessment')?.addEventListener('click', () => openModal('modal-assessment'));
    document.getElementById('btn-open-plugin-modal')?.addEventListener('click', () => openModal('modal-plugin'));
    document.getElementById('btn-open-eval-modal')?.addEventListener('click', () => openModal('modal-experiment'));
}

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = 'flex';
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = 'none';
}

// Load data across all features
async function loadAllData() {
    await Promise.all([
        loadFinOpsOverview(),
        loadSpendBreakdowns(),
        loadOnboardings(),
        loadPolicyProfiles(),
        loadScorecards(),
        loadGoldenTasks(),
        loadEvidenceRecords(),
        loadEvaluations(),
        loadPlugins(),
        loadFleetPosture(),
        loadSDLCFeedback()
    ]);
}

// 1. FinOps Overview & Controls (P1)
async function loadFinOpsOverview() {
    try {
        const res = await fetch('/api/v1/finops/overview');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('kpi-total-spend').textContent = `$${data.total_spend_usd.toFixed(2)}`;
        document.getElementById('kpi-monthly-cap').textContent = `$${data.monthly_budget_cap_usd.toFixed(2)}`;
        document.getElementById('kpi-cost-accepted').textContent = `$${data.cost_per_accepted_task.toFixed(2)}`;
        document.getElementById('kpi-accepted-count').textContent = data.accepted_tasks;
        document.getElementById('kpi-wasted-spend').textContent = `$${data.total_wasted_spend_usd.toFixed(2)}`;
        document.getElementById('kpi-wasted-pct').textContent = `${data.wasted_spend_ratio_pct}%`;
        document.getElementById('kpi-distil-savings').textContent = `$${data.distil_gross_savings_usd.toFixed(2)}`;
        document.getElementById('kpi-distil-roi').textContent = `${data.compression_roi_ratio}x`;

        const badge = document.getElementById('budget-util-badge');
        if (badge) {
            badge.textContent = `${data.budget_utilization_pct}%`;
        }

        const ksStatus = document.getElementById('sidebar-ks-status');
        const quickKillBtn = document.getElementById('btn-quick-kill');
        if (ksStatus) {
            if (data.kill_switch_active) {
                ksStatus.textContent = 'ACTIVE (HALTED)';
                ksStatus.style.color = '#fb7185';
                if (quickKillBtn) quickKillBtn.textContent = 'Resume Fleet';
            } else {
                ksStatus.textContent = 'OFFLINE (Normal)';
                ksStatus.style.color = '#34d399';
                if (quickKillBtn) quickKillBtn.textContent = 'Emergency Halt';
            }
        }
    } catch (e) {
        console.error('Error loading FinOps overview:', e);
    }
}

async function loadSpendBreakdowns() {
    try {
        const [repoRes, modelRes] = await Promise.all([
            fetch('/api/v1/finops/breakdown/repository'),
            fetch('/api/v1/finops/breakdown/model')
        ]);

        if (repoRes.ok) {
            const repos = await repoRes.json();
            const tbody = document.getElementById('tbody-repo-spend');
            if (tbody) {
                tbody.innerHTML = repos.map(r => `
                    <tr>
                        <td><strong>${escapeHtml(r.category)}</strong></td>
                        <td>$${r.total_spend_usd.toFixed(2)}</td>
                        <td><span class="text-emerald">${r.accepted_count}</span></td>
                        <td><span class="text-rose">${r.failed_count}</span></td>
                        <td>$${r.wasted_spend_usd.toFixed(2)}</td>
                        <td>$${r.avg_task_cost_usd.toFixed(2)}</td>
                    </tr>
                `).join('') || '<tr><td colspan="6">No repository records.</td></tr>';
            }
        }

        if (modelRes.ok) {
            const models = await modelRes.json();
            const tbody = document.getElementById('tbody-model-spend');
            if (tbody) {
                tbody.innerHTML = models.map(m => {
                    const total = m.accepted_count + m.failed_count;
                    const succRate = total > 0 ? Math.round((m.accepted_count / total) * 100) : 100;
                    return `
                        <tr>
                            <td><code>${escapeHtml(m.category)}</code></td>
                            <td>$${m.total_spend_usd.toFixed(2)}</td>
                            <td>${total}</td>
                            <td><span class="${succRate >= 90 ? 'text-emerald' : 'text-rose'}">${succRate}%</span></td>
                            <td>$${m.avg_task_cost_usd.toFixed(2)}</td>
                        </tr>
                    `;
                }).join('') || '<tr><td colspan="5">No model records.</td></tr>';
            }
        }
    } catch (e) {
        console.error('Error loading spend breakdowns:', e);
    }
}

// 2. Self-Service Onboarding (P0)
async function loadOnboardings() {
    try {
        const res = await fetch('/api/v1/onboarding/list');
        if (!res.ok) return;
        const items = await res.json();
        const tbody = document.getElementById('tbody-onboarded-list');
        if (!tbody) return;

        tbody.innerHTML = items.map(i => `
            <tr>
                <td><strong>${escapeHtml(i.developer_id)}</strong></td>
                <td><code>${escapeHtml(i.repository)}</code></td>
                <td>${escapeHtml(i.environment_type)}</td>
                <td><span class="status-pill status-active">${escapeHtml(i.data_classification)}</span></td>
                <td>$${i.budget_cap_usd.toFixed(2)}</td>
                <td><span class="status-pill status-${i.status}">${escapeHtml(i.status)}</span></td>
            </tr>
        `).join('') || '<tr><td colspan="6">No onboarded developers.</td></tr>';
    } catch (e) {
        console.error('Error loading onboardings:', e);
    }
}

// 3. Enterprise Policy Profiles (P0)
async function loadPolicyProfiles() {
    try {
        const res = await fetch('/api/v1/policy-profiles/list');
        if (!res.ok) return;
        const profiles = await res.json();
        const tbody = document.getElementById('tbody-policy-profiles');
        if (!tbody) return;

        tbody.innerHTML = profiles.map(p => `
            <tr>
                <td><strong>${escapeHtml(p.name)}</strong></td>
                <td><span class="status-pill status-active">${escapeHtml(p.repo_sensitivity)}</span></td>
                <td>${escapeHtml(p.environment)}</td>
                <td><span class="status-pill status-${p.task_risk === 'critical' ? 'failed' : 'active'}">${escapeHtml(p.task_risk)}</span></td>
                <td><strong>$${p.compass_max_usd.toFixed(2)}</strong></td>
                <td><code>${escapeHtml(p.distil_compression_mode)}</code></td>
                <td><code>${escapeHtml(p.halos_ring)}</code></td>
                <td>${p.require_specialist_review ? '⚠️ Yes' : 'No'}</td>
                <td><code title="${escapeHtml(p.signature)}">${escapeHtml(p.signature.slice(0, 16))}...</code></td>
            </tr>
        `).join('') || '<tr><td colspan="9">No policy profiles.</td></tr>';
    } catch (e) {
        console.error('Error loading policy profiles:', e);
    }
}

// 4. Repository Qualification (P0)
async function loadScorecards() {
    try {
        const res = await fetch('/api/v1/qualification/scorecards');
        if (!res.ok) return;
        const cards = await res.json();
        const container = document.getElementById('qualification-cards-container');
        if (!container) return;

        container.innerHTML = cards.map(c => `
            <div class="scorecard-card">
                <div class="scorecard-header">
                    <div>
                        <h3>${escapeHtml(c.repository)}</h3>
                        <span class="card-badge">Owner: ${escapeHtml(c.owner)}</span>
                    </div>
                    <div class="score-badge ${c.score >= 80 ? 'score-pass' : 'score-fail'}">
                        <span>${c.score}</span>
                    </div>
                </div>
                <div class="scorecard-meta">
                    <p>Tests: <strong>${escapeHtml(c.test_suite_status)}</strong></p>
                    <p>Branch Protection: <strong>${c.branch_protection ? 'Enforced' : 'Missing ⚠️'}</strong></p>
                    <p>CODEOWNERS: <strong>${c.codeowners_present ? 'Present' : 'Missing'}</strong></p>
                    <p>Unapproved MCPs: <strong>${c.unapproved_mcp_count}</strong></p>
                    <p>Billing Owner: <strong>${c.billing_owner_defined ? 'Defined' : 'Missing ⚠️'}</strong></p>
                </div>
                ${c.blockers && c.blockers.length > 0 ? `
                    <div class="scorecard-blockers">
                        <strong>Actionable Blockers:</strong>
                        <ul style="padding-left: 16px; margin-top: 4px;">
                            ${c.blockers.map(b => `<li>${escapeHtml(b)}</li>`).join('')}
                        </ul>
                    </div>
                ` : `
                    <div style="font-size:0.8rem; color:#34d399;">
                        ✅ Qualified for AI-assisted coding under Halos ring policy.
                    </div>
                `}
            </div>
        `).join('') || '<p>No repositories qualified.</p>';
    } catch (e) {
        console.error('Error loading scorecards:', e);
    }
}

// 5. Golden-Path Tasks (P0)
async function loadGoldenTasks() {
    try {
        const res = await fetch('/api/v1/golden-tasks/catalog');
        if (!res.ok) return;
        const tasks = await res.json();

        const container = document.getElementById('golden-catalog-items');
        const select = document.getElementById('launch-template-select');

        if (container) {
            container.innerHTML = tasks.map(t => `
                <div class="catalog-item">
                    <div>
                        <h4>${escapeHtml(t.name)}</h4>
                        <p style="font-size:0.8rem; color:var(--text-secondary);">${escapeHtml(t.description)}</p>
                        <span class="card-badge" style="margin-top:6px; display:inline-block;">
                            Class: ${escapeHtml(t.task_class)} • Risk: ${escapeHtml(t.risk_level)} • Human Merge: ${t.require_human_merge ? 'Yes' : 'Auto'}
                        </span>
                    </div>
                    <div style="text-align:right;">
                        <strong style="color:#a5b4fc;">$${t.standard_budget_usd.toFixed(2)}</strong> cap
                        <div style="font-size:0.75rem; color:var(--text-muted);">${t.execution_count} runs (${Math.round(t.success_rate * 100)}% pass)</div>
                    </div>
                </div>
            `).join('');
        }

        if (select) {
            select.innerHTML = tasks.map(t => `
                <option value="${t.id}">${escapeHtml(t.name)} ($${t.standard_budget_usd.toFixed(2)} cap)</option>
            `).join('');
        }
    } catch (e) {
        console.error('Error loading golden tasks:', e);
    }
}

// 6. Unified Task Evidence Record (P0)
async function loadEvidenceRecords() {
    try {
        const res = await fetch('/api/v1/evidence/records');
        if (!res.ok) return;
        const records = await res.json();
        const tbody = document.getElementById('tbody-evidence-records');
        if (!tbody) return;

        tbody.innerHTML = records.map(r => `
            <tr>
                <td><strong>${escapeHtml(r.work_item)}</strong></td>
                <td><code>${escapeHtml(r.repository)}</code></td>
                <td><code>${escapeHtml(r.base_commit)}</code></td>
                <td>${escapeHtml(r.model_name)}</td>
                <td><code>${escapeHtml(r.halos_release_id)}</code></td>
                <td>$${r.billed_cost_usd.toFixed(2)}</td>
                <td><span class="text-cyan">+$${r.distil_savings_usd.toFixed(2)}</span></td>
                <td>${r.pr_number ? `#${r.pr_number}` : '-'}</td>
                <td>${r.human_approver ? escapeHtml(r.human_approver) : 'System'}</td>
                <td><span class="status-pill status-${r.merge_outcome}">${escapeHtml(r.merge_outcome)}</span></td>
            </tr>
        `).join('') || '<tr><td colspan="10">No evidence records.</td></tr>';
    } catch (e) {
        console.error('Error loading evidence records:', e);
    }
}

// 7. Enterprise Evaluations (P1)
async function loadEvaluations() {
    try {
        const res = await fetch('/api/v1/evaluations/history');
        if (!res.ok) return;
        const evals = await res.json();
        const tbody = document.getElementById('tbody-evaluations');
        if (!tbody) return;

        tbody.innerHTML = evals.map(e => `
            <tr>
                <td><strong>${escapeHtml(e.experiment_name)}</strong></td>
                <td><code>${escapeHtml(e.tool_combination)}</code></td>
                <td>${escapeHtml(e.model_candidate)}</td>
                <td><strong>${(e.pass_at_k * 100).toFixed(1)}%</strong></td>
                <td>$${e.cost_per_accepted_task.toFixed(2)}</td>
                <td>${e.avg_completion_time_sec.toFixed(1)}s</td>
                <td>${e.security_regressions === 0 ? '0 ✅' : `${e.security_regressions} ⚠️`}</td>
                <td><span class="status-pill status-${e.verdict.includes('QUALIFIED') || e.verdict.includes('PROMOTED') ? 'approved' : 'failed'}">${escapeHtml(e.verdict)}</span></td>
            </tr>
        `).join('') || '<tr><td colspan="8">No evaluation records.</td></tr>';
    } catch (e) {
        console.error('Error loading evaluations:', e);
    }
}

// 8. Governed Plugins (P1)
async function loadPlugins() {
    try {
        const res = await fetch('/api/v1/plugins/list');
        if (!res.ok) return;
        const plugins = await res.json();
        const tbody = document.getElementById('tbody-plugins');
        if (!tbody) return;

        tbody.innerHTML = plugins.map(p => `
            <tr>
                <td><strong>${escapeHtml(p.name)}</strong></td>
                <td><code>${escapeHtml(p.version)}</code></td>
                <td>${escapeHtml(p.owner)}</td>
                <td>${p.permissions.map(perm => `<code style="font-size:0.75rem;">${escapeHtml(perm)}</code>`).join(' ')}</td>
                <td>${p.data_destinations.join(', ')}</td>
                <td><strong class="${p.scan_score >= 80 ? 'text-emerald' : 'text-rose'}">${p.scan_score}/100</strong></td>
                <td><span class="status-pill status-${p.status}">${escapeHtml(p.status)}</span></td>
                <td>
                    ${p.status === 'approved' ? `
                        <button class="btn btn-sm btn-danger-outline" onclick="togglePlugin('${p.id}', 'revoked')">Revoke</button>
                    ` : `
                        <button class="btn btn-sm btn-secondary" onclick="togglePlugin('${p.id}', 'approved')">Approve</button>
                    `}
                </td>
            </tr>
        `).join('') || '<tr><td colspan="8">No plugins registered.</td></tr>';
    } catch (e) {
        console.error('Error loading plugins:', e);
    }
}

window.togglePlugin = async function(id, newStatus) {
    try {
        await fetch(`/api/v1/plugins/${id}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus, reason: 'Operator action via dashboard' })
        });
        loadPlugins();
    } catch (e) {
        alert('Failed to update plugin status: ' + e);
    }
};

// 9. Fleet Posture & Drift (P1)
async function loadFleetPosture() {
    try {
        const res = await fetch('/api/v1/fleet/summary');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('fleet-total-nodes').textContent = data.total_nodes;
        document.getElementById('fleet-healthy-nodes').textContent = data.healthy_nodes;
        document.getElementById('fleet-drift-nodes').textContent = data.drifted_nodes;
        document.getElementById('fleet-compliance-pct').textContent = `${data.compliance_rate_pct}%`;

        const tbody = document.getElementById('tbody-fleet-nodes');
        if (!tbody) return;

        tbody.innerHTML = data.nodes.map(n => `
            <tr>
                <td><code>${escapeHtml(n.node_id)}</code></td>
                <td><strong>${escapeHtml(n.developer_id)}</strong></td>
                <td>${escapeHtml(n.cli_name)}</td>
                <td><code>${escapeHtml(n.installed_version)}</code></td>
                <td><code>${escapeHtml(n.pinned_version)}</code></td>
                <td><code>${escapeHtml(n.ring)}</code></td>
                <td><span class="status-pill status-${n.status}">${escapeHtml(n.status)}</span></td>
                <td>
                    ${n.drift_detected ? `
                        <button class="btn btn-sm btn-primary" onclick="remediateDrift('${n.node_id}')">Fix Drift</button>
                    ` : `<span style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(n.remediation || 'OK')}</span>`}
                </td>
            </tr>
        `).join('') || '<tr><td colspan="8">No fleet nodes registered.</td></tr>';
    } catch (e) {
        console.error('Error loading fleet posture:', e);
    }
}

window.remediateDrift = async function(nodeId) {
    try {
        await fetch('/api/v1/fleet/remediate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ node_id: nodeId, force_update_to_pinned: true })
        });
        loadFleetPosture();
    } catch (e) {
        alert('Failed to remediate node: ' + e);
    }
};

// 10. SDLC Feedback Loop (P2)
async function loadSDLCFeedback() {
    try {
        const res = await fetch('/api/v1/feedback/patterns');
        if (!res.ok) return;
        const patterns = await res.json();
        const tbody = document.getElementById('tbody-feedback-patterns');
        if (!tbody) return;

        tbody.innerHTML = patterns.map(p => `
            <tr>
                <td><strong>${escapeHtml(p.failure_pattern)}</strong></td>
                <td><span class="status-pill status-failed">${p.occurrences} failures</span></td>
                <td><code>${escapeHtml(p.affected_repositories)}</code></td>
                <td>${escapeHtml(p.suggested_improvement)}</td>
                <td><span class="status-pill status-${p.status}">${escapeHtml(p.status)}</span></td>
                <td>
                    ${p.status !== 'pr_generated' ? `
                        <button class="btn btn-sm btn-primary" onclick="generatePolicyPR('${p.id}')">Create Policy PR</button>
                    ` : `<span style="font-size:0.75rem; color:#34d399;">PR #108 Awaiting Merge</span>`}
                </td>
            </tr>
        `).join('') || '<tr><td colspan="6">No recurring failure patterns detected.</td></tr>';
    } catch (e) {
        console.error('Error loading SDLC feedback:', e);
    }
}

window.generatePolicyPR = async function(feedbackId) {
    try {
        const res = await fetch('/api/v1/feedback/generate-pr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ feedback_id: feedbackId, target_ring: 'canary_1' })
        });
        const data = await res.json();
        alert(`Policy Improvement PR created: ${data.pr_url}\nTarget Ring: ${data.target_ring}`);
        loadSDLCFeedback();
    } catch (e) {
        alert('Failed to generate policy PR: ' + e);
    }
};

// Form Initializations
function initForms() {
    // Onboarding Form
    const onbForm = document.getElementById('form-onboarding');
    if (onbForm) {
        onbForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('btn-submit-onboard');
            const feedback = document.getElementById('onboarding-live-feedback');
            btn.disabled = true;
            btn.textContent = 'Enrolling in Halos & Running Compass Verification...';
            feedback.style.display = 'block';
            feedback.textContent = '1/3 Enrolling entity in Halos fleet... 2/3 Setting Compass session budget cap... 3/3 Running bounded verification test...';

            try {
                const payload = {
                    developer_id: document.getElementById('onb-dev-id').value,
                    repository: document.getElementById('onb-repo').value,
                    environment_type: document.getElementById('onb-env').value,
                    data_classification: document.getElementById('onb-data-class').value,
                    monthly_budget_cap_usd: parseFloat(document.getElementById('onb-budget').value),
                    target_ring: document.getElementById('onb-ring').value
                };

                const res = await fetch('/api/v1/onboarding/enroll', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                feedback.innerHTML = `
                    ✅ <strong>Enrollment Complete!</strong><br>
                    • Halos Signed Token: <code>${data.halos_token}</code><br>
                    • Compass Budget Cap: <strong>$${data.budget_cap_usd}</strong><br>
                    • Verification Task: <strong>${data.verification_evidence.status}</strong> ($${data.verification_evidence.cost_usd.toFixed(2)})<br>
                    • Human Merge Gate: <strong>Verified</strong>
                `;
                loadOnboardings();
                loadFinOpsOverview();
            } catch (err) {
                feedback.innerHTML = `❌ Error: ${err}`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Run Intake & Bounded Verification Task';
            }
        });
    }

    // Launch Task Form
    const launchForm = document.getElementById('form-launch-task');
    if (launchForm) {
        launchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('btn-execute-task');
            const terminal = document.getElementById('task-live-output');
            btn.disabled = true;
            btn.textContent = 'Executing Bounded Task in Compass...';
            terminal.style.display = 'block';
            terminal.textContent = '>>> Initializing Compass sandbox...\n>>> Applying COMPASS_MAX_USD guardrail...\n>>> Invoking Distil lossless compression...\n';

            try {
                const payload = {
                    task_template_id: document.getElementById('launch-template-select').value,
                    repository: document.getElementById('launch-repo').value,
                    developer_id: 'dev_current_session',
                    work_item: document.getElementById('launch-work-item').value,
                    task_prompt: document.getElementById('launch-prompt').value
                };

                const res = await fetch('/api/v1/golden-tasks/launch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                terminal.textContent += `>>> Status: ${data.status.toUpperCase()}\n>>> Cost Spent: $${data.cost_spent_usd.toFixed(2)} (Cap: $${data.budget_cap_usd.toFixed(2)})\n>>> Iterations: ${data.iterations}\n>>> Human Merge Gate: ${data.human_merge_required ? 'ENFORCED (You always merge)' : 'AUTO'}\n>>> Evidence Token: ${data.evidence_token}\n>>> Result: ${data.message}\n`;

                loadFinOpsOverview();
                loadSpendBreakdowns();
                loadEvidenceRecords();
                loadGoldenTasks();
            } catch (err) {
                terminal.textContent += `>>> FATAL: ${err}\n`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Execute Bounded Task';
            }
        });
    }

    // Budget Cap Form
    const budgetForm = document.getElementById('form-update-budget');
    if (budgetForm) {
        budgetForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                scope: document.getElementById('budget-scope').value,
                new_budget_cap_usd: parseFloat(document.getElementById('budget-new-cap').value),
                alert_threshold_pct: parseFloat(document.getElementById('budget-threshold').value)
            };
            try {
                await fetch('/api/v1/finops/budget/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                closeModal('modal-budget');
                loadFinOpsOverview();
            } catch (err) {
                alert('Failed to update budget: ' + err);
            }
        });
    }

    // Kill Switch Form
    const ksForm = document.getElementById('form-kill-switch');
    if (ksForm) {
        ksForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                activate: document.getElementById('ks-action-select').value === 'true',
                reason: document.getElementById('ks-reason').value
            };
            try {
                await fetch('/api/v1/finops/kill-switch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                closeModal('modal-kill');
                loadFinOpsOverview();
            } catch (err) {
                alert('Kill switch action failed: ' + err);
            }
        });
    }

    // Repo Assessment Form
    const evalRepoForm = document.getElementById('form-eval-repo');
    if (evalRepoForm) {
        evalRepoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                repository: document.getElementById('eval-repo-name').value,
                owner: document.getElementById('eval-owner').value
            };
            try {
                await fetch('/api/v1/qualification/assess', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                closeModal('modal-assessment');
                loadScorecards();
            } catch (err) {
                alert('Assessment failed: ' + err);
            }
        });
    }

    // Plugin Form
    const plgForm = document.getElementById('form-register-plugin');
    if (plgForm) {
        plgForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById('reg-plg-name').value,
                version: document.getElementById('reg-plg-version').value,
                owner: document.getElementById('reg-plg-owner').value,
                permissions: document.getElementById('reg-plg-perms').value.split(',').map(s => s.trim()),
                data_destinations: document.getElementById('reg-plg-dests').value.split(',').map(s => s.trim())
            };
            try {
                await fetch('/api/v1/plugins/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                closeModal('modal-plugin');
                loadPlugins();
            } catch (err) {
                alert('Plugin registration failed: ' + err);
            }
        });
    }

    // Experiment Form
    const expForm = document.getElementById('form-run-experiment');
    if (expForm) {
        expForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                experiment_name: document.getElementById('exp-name').value,
                candidate_model: document.getElementById('exp-model').value,
                tool_combination: document.getElementById('exp-stack').value,
                sample_size: parseInt(document.getElementById('exp-samples').value, 10)
            };
            try {
                await fetch('/api/v1/evaluations/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                closeModal('modal-experiment');
                loadEvaluations();
            } catch (err) {
                alert('Experiment run failed: ' + err);
            }
        });
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
