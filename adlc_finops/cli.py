"""Command Line Interface (CLI) for ADLC FinOps Platform."""

import sys
import argparse
import json
from adlc_finops.features_facade import (
    get_finops_overview,
    update_budget_cap,
    toggle_kill_switch,
    onboard_entity,
    assess_repository,
    launch_golden_task,
    get_fleet_summary,
    list_governed_plugins,
    run_eval_experiment
)

def main():
    parser = argparse.ArgumentParser(
        prog="adlc-finops",
        description="ADLC FinOps & Governance CLI: Consumes Compass, Distil, and Halos APIs."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # FinOps Subcommands
    finops_parser = subparsers.add_parser("finops", help="FinOps metrics and budget management")
    finops_sub = finops_parser.add_subparsers(dest="subcommand")

    finops_sub.add_parser("summary", help="Show overarching FinOps KPI summary")

    budget_p = finops_sub.add_parser("budget", help="Set monthly budget cap")
    budget_p.add_argument("--cap", type=float, required=True, help="New budget cap in USD")
    budget_p.add_argument("--scope", default="global", help="Scope: global or repository name")

    ks_p = finops_sub.add_parser("kill-switch", help="Trigger or deactivate fleet kill switch")
    ks_p.add_argument("--activate", action="store_true", help="Activate emergency kill switch")
    ks_p.add_argument("--deactivate", action="store_true", help="Deactivate kill switch")
    ks_p.add_argument("--reason", required=True, help="Reason for kill switch action")

    # Onboarding Subcommand
    onb_p = subparsers.add_parser("onboard", help="Enroll developer & repository into governed platform")
    onb_p.add_argument("--developer", required=True, help="Developer SSO ID")
    onb_p.add_argument("--repo", required=True, help="Repository name")
    onb_p.add_argument("--budget", type=float, default=500.0, help="Monthly budget cap in USD")
    onb_p.add_argument("--ring", default="canary_5", help="Rollout ring (canary_1, canary_5, stage_25, ga_100)")

    # Qualification Subcommand
    qual_p = subparsers.add_parser("qualify", help="Assess repository readiness for AI agents")
    qual_p.add_argument("--repo", required=True, help="Repository name")
    qual_p.add_argument("--owner", required=True, help="Billing / engineering owner")

    # Task Launch Subcommand
    task_p = subparsers.add_parser("task", help="Execute golden-path task")
    task_p.add_argument("--template", required=True, help="Template ID (e.g. task-unit-bug)")
    task_p.add_argument("--repo", required=True, help="Repository name")
    task_p.add_argument("--prompt", required=True, help="Task prompt / instructions")
    task_p.add_argument("--work-item", default="CLI-TASK-01", help="Work item ticket ID")

    # Fleet Subcommand
    subparsers.add_parser("fleet", help="Inspect fleet posture and drift")

    # Plugins Subcommand
    subparsers.add_parser("plugins", help="List governed plugins and scan status")

    # Server Subcommand
    server_p = subparsers.add_parser("server", help="Start the FastAPI web server & dashboard")
    server_p.add_argument("--host", default="0.0.0.0", help="Bind host")
    server_p.add_argument("--port", type=int, default=8000, help="Bind port")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "finops":
        if args.subcommand == "summary":
            overview = get_finops_overview()
            print("==================================================")
            print("  ADLC FINOPS CONTROL PLANE - SUMMARY")
            print("==================================================")
            print(f"Total Net Spend:            ${overview.total_spend_usd:,.2f}")
            print(f"Monthly Budget Cap:         ${overview.monthly_budget_cap_usd:,.2f} ({overview.budget_utilization_pct}% utilized)")
            print(f"Cost per Accepted Task:     ${overview.cost_per_accepted_task:,.2f}")
            print(f"Accepted Tasks:             {overview.accepted_tasks} / {overview.total_tasks}")
            print(f"Wasted Spend (Failed):      ${overview.total_wasted_spend_usd:,.2f} ({overview.wasted_spend_ratio_pct}%)")
            print(f"Distil Gross Savings:       ${overview.distil_gross_savings_usd:,.2f}")
            print(f"Distil Compression ROI:     {overview.compression_roi_ratio}x")
            print(f"Emergency Kill Switch:      {'ACTIVE (HALTED)' if overview.kill_switch_active else 'OFFLINE (Normal)'}")
            print("==================================================")
        elif args.subcommand == "budget":
            res = update_budget_cap(scope=args.scope, new_cap_usd=args.cap)
            print(f"Budget cap updated for scope '{args.scope}': ${args.cap:,.2f}")
            print(f"Enforcement: {res['enforcement']}")
        elif args.subcommand == "kill-switch":
            act = args.activate and not args.deactivate
            res = toggle_kill_switch(activate=act, reason=args.reason)
            status_str = "ACTIVATED (HALTED)" if res.active else "DEACTIVATED (NORMAL)"
            print(f"Kill Switch {status_str}: {res.reason}")
            print(f"Signed Token: {res.signed_token} | Propagation: {res.propagation_time_sec}s across {res.gateways_notified} gateways")

    elif args.command == "onboard":
        res = onboard_entity(args.developer, args.repo, args.budget, args.ring)
        print("Developer & Repository Onboarded:")
        print(f"ID:           {res.onboarding_id}")
        print(f"Halos Token:  {res.halos_token}")
        print(f"Compass Token: {res.compass_session_token}")
        print(f"Budget Cap:   ${res.budget_cap_usd:,.2f}")
        print(f"Verification: {res.verification_evidence.status} (${res.verification_evidence.cost_usd:,.2f})")

    elif args.command == "qualify":
        card = assess_repository(args.repo, args.owner)
        status = "PASSED" if card.is_qualified else "FAILED"
        print(f"Qualification Scorecard for {card.repository}: {card.score}/100 [{status}]")
        print(f"Test Status:        {card.test_suite_status}")
        print(f"Branch Protection:  {'Yes' if card.branch_protection else 'No (BLOCKER)'}")
        print(f"Unapproved MCPs:    {card.unapproved_mcp_count}")
        if card.blockers:
            print("\nActionable Blockers:")
            for b in card.blockers:
                print(f" - {b}")

    elif args.command == "task":
        res = launch_golden_task(args.template, args.repo, args.prompt, args.work_item)
        print(f"Task ID: {res.task_id} [{res.status.value.upper()}]")
        print(f"Cost:    ${res.cost_spent_usd:,.2f} / Cap: ${res.budget_cap_usd:,.2f}")
        print(f"Human Merge Gate: {'Enforced (You always merge)' if res.human_merge_required else 'Automated'}")
        print(f"Message: {res.message}")

    elif args.command == "fleet":
        summary = get_fleet_summary()
        print(f"Fleet Posture: {summary.healthy_nodes}/{summary.total_nodes} Healthy ({summary.compliance_rate_pct}% Compliance)")
        for n in summary.nodes:
            flag = "[DRIFT]" if n.drift_detected else "[OK]"
            print(f" {flag} {n.node_id:20} {n.developer_id:15} {n.cli_name:12} v{n.installed_version} (Pinned: v{n.pinned_version}) Ring: {n.ring}")

    elif args.command == "plugins":
        plugins = list_governed_plugins()
        print(f"Governed Plugins ({len(plugins)} total):")
        for p in plugins:
            print(f" - [{p.status.upper()}] {p.name} v{p.version} (Score: {p.scan_score}/100) Owner: {p.owner}")

    elif args.command == "server":
        import uvicorn
        print(f"Starting ADLC FinOps Server on {args.host}:{args.port}...")
        uvicorn.run("adlc_finops.server:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()
