"""Database and persistence layer for ADLC FinOps platform."""

import sqlite3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from .config import settings

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.db_path
        self._init_db()
        self._seed_initial_data()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Onboardings table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS onboardings (
                id TEXT PRIMARY KEY,
                developer_id TEXT NOT NULL,
                repository TEXT NOT NULL,
                environment_type TEXT NOT NULL,
                data_classification TEXT NOT NULL,
                assigned_profile_id TEXT NOT NULL,
                budget_cap_usd REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """)

            # Policy profiles
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS policy_profiles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                repo_sensitivity TEXT NOT NULL,
                environment TEXT NOT NULL,
                task_risk TEXT NOT NULL,
                compass_max_usd REAL NOT NULL,
                distil_compression_mode TEXT NOT NULL,
                halos_ring TEXT NOT NULL,
                require_specialist_review INTEGER NOT NULL,
                allowed_commands TEXT NOT NULL,
                signature TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """)

            # Qualification scorecards
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS qualification_scorecards (
                repository TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                score INTEGER NOT NULL,
                is_qualified INTEGER NOT NULL,
                test_suite_status TEXT NOT NULL,
                branch_protection INTEGER NOT NULL,
                codeowners_present INTEGER NOT NULL,
                unapproved_mcp_count INTEGER NOT NULL,
                billing_owner_defined INTEGER NOT NULL,
                blockers TEXT NOT NULL,
                evaluated_at TEXT NOT NULL
            )
            """)

            # Golden path tasks
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS golden_tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                task_class TEXT NOT NULL,
                description TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                standard_budget_usd REAL NOT NULL,
                require_human_merge INTEGER NOT NULL,
                execution_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0
            )
            """)

            # Unified evidence records
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_records (
                task_id TEXT PRIMARY KEY,
                work_item TEXT NOT NULL,
                repository TEXT NOT NULL,
                base_commit TEXT NOT NULL,
                developer_id TEXT NOT NULL,
                agent_identity TEXT NOT NULL,
                compass_policy_hash TEXT NOT NULL,
                halos_release_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                distil_receipt_id TEXT NOT NULL,
                billed_cost_usd REAL NOT NULL,
                tokens_saved INTEGER NOT NULL,
                distil_savings_usd REAL NOT NULL,
                test_passed INTEGER NOT NULL,
                pr_number INTEGER,
                human_approver TEXT,
                merge_outcome TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """)

            # Enterprise evaluations
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id TEXT PRIMARY KEY,
                experiment_name TEXT NOT NULL,
                tool_combination TEXT NOT NULL,
                model_candidate TEXT NOT NULL,
                pass_at_k REAL NOT NULL,
                cost_per_accepted_task REAL NOT NULL,
                avg_completion_time_sec REAL NOT NULL,
                security_regressions INTEGER NOT NULL,
                verdict TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """)

            # FinOps Ledger / Transactions
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS finops_ledger (
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
            )
            """)

            # Governed MCP / Plugins
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS governed_plugins (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                owner TEXT NOT NULL,
                permissions TEXT NOT NULL,
                data_destinations TEXT NOT NULL,
                status TEXT NOT NULL,
                scan_score INTEGER NOT NULL,
                added_at TEXT NOT NULL
            )
            """)

            # Fleet Posture & Drift
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fleet_nodes (
                node_id TEXT PRIMARY KEY,
                developer_id TEXT NOT NULL,
                cli_name TEXT NOT NULL,
                installed_version TEXT NOT NULL,
                pinned_version TEXT NOT NULL,
                ring TEXT NOT NULL,
                drift_detected INTEGER NOT NULL,
                last_heartbeat TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """)

            # SDLC Feedback loops
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_items (
                id TEXT PRIMARY KEY,
                failure_pattern TEXT NOT NULL,
                occurrences INTEGER NOT NULL,
                affected_repositories TEXT NOT NULL,
                suggested_improvement TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """)

            # System settings (e.g. kill switch)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_controls (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """)
            conn.commit()

    def _seed_initial_data(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM policy_profiles")
            if cursor.fetchone()["cnt"] > 0:
                return  # already seeded

            now = datetime.now(timezone.utc).isoformat()

            # Seed System Controls
            cursor.execute("INSERT OR REPLACE INTO system_controls VALUES (?, ?, ?)",
                           ("kill_switch_active", "false", now))
            cursor.execute("INSERT OR REPLACE INTO system_controls VALUES (?, ?, ?)",
                           ("monthly_budget_cap", "50000.00", now))

            # Seed Policy Profiles
            profiles = [
                ("prof-standard-dev", "Standard Internal Dev", "internal", "local_workstation", "medium", 5.0, "lossless", "canary_5", 0,
                 json.dumps(["pytest", "git status", "git diff", "npm test", "ruff check"]), "ed25519:pol-8a9b0c", now),
                ("prof-critical-auth", "High Risk / Critical Infra", "confidential", "dev_container", "critical", 15.0, "lossless", "stage_25", 1,
                 json.dumps(["pytest -m security", "git status", "trivy fs"]), "ed25519:pol-7711aa", now),
                ("prof-ci-automation", "CI Autonomous Fixer", "internal", "ci_runner", "low", 3.0, "aggressive", "ga_100", 0,
                 json.dumps(["pytest", "flake8", "black --check"]), "ed25519:pol-9922ff", now)
            ]
            cursor.executemany("""
                INSERT INTO policy_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, profiles)

            # Seed Golden Tasks
            tasks = [
                ("task-doc-fix", "Documentation & Typo Fix", "Documentation", "Bounded doc updates and markdown cleanup", "low", 1.50, 0, 42, 0.98),
                ("task-unit-bug", "Repro & Unit Bug Fix", "Test & Bug Fix", "Reproduce failing test, preserve test suite, apply fix", "medium", 4.00, 1, 88, 0.93),
                ("task-dep-upgrade", "Dependency Security Patch", "Dependencies", "Update vulnerable dependency, run CVE scanners and suite", "high", 6.50, 1, 26, 0.88),
                ("task-refactor-lint", "Clean Code Refactoring", "Refactoring", "Approved style and structure cleanup with 100% test preservation", "medium", 3.50, 1, 35, 0.95),
                ("task-auth-hardening", "Auth & Token Hardening", "Security & Auth", "Audit token lifecycle and rotate secret validations", "critical", 12.00, 1, 14, 0.86)
            ]
            cursor.executemany("""
                INSERT INTO golden_tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tasks)

            # Seed Repository Qualifications
            repos = [
                ("wideanchorgroup/ADLC-TokenModules", "platform-core", 92, 1, "passing_100_pct", 1, 1, 0, 1, json.dumps([]), now),
                ("wideanchorgroup/auth-service", "security-team", 88, 1, "passing_98_pct", 1, 1, 0, 1, json.dumps([]), now),
                ("wideanchorgroup/legacy-billing", "payments-team", 54, 0, "failing_tests_3_errors", 0, 1, 2, 0,
                 json.dumps(["Missing branch protection", "Failing legacy test suite (3 errors)", "Unapproved MCP curl plugin installed", "No defined billing owner"]), now),
                ("wideanchorgroup/data-pipelines", "data-eng", 75, 1, "passing_95_pct", 1, 0, 0, 1,
                 json.dumps(["CODEOWNERS file missing"]), now)
            ]
            cursor.executemany("""
                INSERT INTO qualification_scorecards VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, repos)

            # Seed Onboardings
            onboardings = [
                ("onb-001", "dev_alice", "wideanchorgroup/ADLC-TokenModules", "local_workstation", "internal", "prof-standard-dev", 500.0, "active", now),
                ("onb-002", "dev_bob", "wideanchorgroup/auth-service", "dev_container", "confidential", "prof-critical-auth", 1200.0, "active", now),
                ("onb-003", "ci_runner_east", "wideanchorgroup/ADLC-TokenModules", "ci_runner", "internal", "prof-ci-automation", 2500.0, "active", now)
            ]
            cursor.executemany("""
                INSERT INTO onboardings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, onboardings)

            # Seed Governed Plugins
            plugins = [
                ("plg-git-tools", "Git Safe Automation", "1.2.0", "dev-sec-ops", json.dumps(["git_read", "git_commit"]), json.dumps(["internal-github"]), "approved", 98, now),
                ("plg-postgres-query", "Readonly DB Inspector", "0.9.1", "data-team", json.dumps(["pg_readonly_query"]), json.dumps(["rds-internal-vpc"]), "approved", 92, now),
                ("plg-unvetted-crawler", "Web Scraper MCP", "0.1.0", "external-contributor", json.dumps(["raw_socket", "unrestricted_fs"]), json.dumps(["external_unknown"]), "revoked", 22, now),
                ("plg-jira-sync", "Atlassian Task Linker", "2.0.4", "product-ops", json.dumps(["http_jira_api"]), json.dumps(["atlassian.net"]), "approved", 95, now)
            ]
            cursor.executemany("""
                INSERT INTO governed_plugins VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, plugins)

            # Seed Fleet Nodes
            fleet = [
                ("node-mac-alice", "dev_alice", "Claude Code", "0.8.4", "0.8.4", "canary_5", 0, now, "healthy"),
                ("node-mac-bob", "dev_bob", "Codex CLI", "2.4.1", "2.4.1", "stage_25", 0, now, "healthy"),
                ("node-linux-charlie", "dev_charlie", "Claude Code", "0.7.1", "0.8.4", "canary_5", 1, now, "drift_detected"),
                ("node-ci-runner1", "ci_runner_east", "Gemini CLI", "1.3.0", "1.3.0", "ga_100", 0, now, "healthy")
            ]
            cursor.executemany("""
                INSERT INTO fleet_nodes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, fleet)

            # Seed Evaluations
            evals = [
                ("eval-001", "Claude 3.7 vs 3.5 on Complex Refactoring", "Compass+Distil(lossless)+Claude-3-7", "anthropic/claude-3-7-sonnet", 0.94, 3.12, 42.5, 0, "PROMOTED_TO_STAGE", now),
                ("eval-002", "Gemini 2.5 Flash on Unit Bug Fix", "Compass+Distil(aggressive)+Gemini-2-5", "google/gemini-2.5-flash", 0.89, 0.85, 18.2, 0, "QUALIFIED_FOR_CANARY", now),
                ("eval-003", "Experimental Unsigned MCP Agent", "Unsigned-Tools+Claude-3-5", "anthropic/claude-3-5-sonnet", 0.61, 8.40, 110.0, 2, "REJECTED_SECURITY_RISK", now)
            ]
            cursor.executemany("""
                INSERT INTO evaluations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evals)

            # Seed FinOps Ledger & Evidence Records
            ledger_items = [
                ("tx-101", now, "wideanchorgroup/ADLC-TokenModules", "dev_alice", "claude-3-7-sonnet", "Test & Bug Fix", 4.10, 1.25, 2.85, 1, None),
                ("tx-102", now, "wideanchorgroup/ADLC-TokenModules", "dev_alice", "claude-3-7-sonnet", "Documentation", 1.80, 0.70, 1.10, 1, None),
                ("tx-103", now, "wideanchorgroup/auth-service", "dev_bob", "claude-3-7-sonnet", "Security & Auth", 9.40, 2.80, 6.60, 1, None),
                ("tx-104", now, "wideanchorgroup/legacy-billing", "dev_charlie", "claude-3-5-sonnet", "Test & Bug Fix", 5.00, 0.00, 5.00, 0, "Compass budget cap halted session at $5.00 ceiling"),
                ("tx-105", now, "wideanchorgroup/ADLC-TokenModules", "ci_runner_east", "gemini-2.5-flash", "Documentation", 0.65, 0.25, 0.40, 1, None),
                ("tx-106", now, "wideanchorgroup/auth-service", "dev_bob", "claude-3-7-sonnet", "Dependencies", 7.20, 2.10, 5.10, 1, None),
                ("tx-107", now, "wideanchorgroup/data-pipelines", "dev_dave", "claude-3-5-sonnet", "Refactoring", 5.00, 0.10, 4.90, 0, "Test suite regression caught; PR rejected")
            ]
            cursor.executemany("""
                INSERT INTO finops_ledger VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ledger_items)

            evidence_items = [
                ("task-ev-101", "JIRA-4812", "wideanchorgroup/ADLC-TokenModules", "a8c91f0", "dev_alice", "agent-claude-c1", "cmp-pol-sha256-44aa", "rel-2026.10.4-signed",
                 "anthropic/claude-3-7-sonnet", "dst-rcpt-8812a", 2.85, 34000, 1.25, 1, 142, "tech-lead-mary", "merged", now),
                ("task-ev-102", "JIRA-4890", "wideanchorgroup/auth-service", "b7d12e4", "dev_bob", "agent-claude-c2", "cmp-pol-sha256-77bb", "rel-2026.10.4-signed",
                 "anthropic/claude-3-7-sonnet", "dst-rcpt-9931b", 6.60, 89000, 2.80, 1, 145, "sec-officer-dan", "merged", now),
                ("task-ev-103", "JIRA-5011", "wideanchorgroup/legacy-billing", "c4f33d1", "dev_charlie", "agent-claude-c3", "cmp-pol-sha256-44aa", "rel-2026.09.28-stable",
                 "anthropic/claude-3-5-sonnet", "dst-rcpt-0012c", 5.00, 2000, 0.00, 0, None, None, "halted_budget", now)
            ]
            cursor.executemany("""
                INSERT INTO evidence_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evidence_items)

            # Seed SDLC Feedback Items
            feedback = [
                ("fb-001", "Agent loop timeout in legacy mock frameworks", 14, "wideanchorgroup/legacy-billing",
                 "Inject explicit mock harness fixtures into Compass review/test prompt template", "in_review", now),
                ("fb-002", "Token budget exhaustion during large file diffs", 8, "wideanchorgroup/data-pipelines",
                 "Tune Distil context windowing to compress test fixture ASTs losslessly", "approved_for_rollout", now),
                ("fb-003", "Developer manually overriding branch protection check", 5, "wideanchorgroup/legacy-billing",
                 "Enforce Halos signed pre-commit hook preventing unverified bypass", "planned", now)
            ]
            cursor.executemany("""
                INSERT INTO feedback_items VALUES (?, ?, ?, ?, ?, ?, ?)
            """, feedback)

            conn.commit()

db = Database()
