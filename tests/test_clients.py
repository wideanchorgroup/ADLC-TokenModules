"""Tests for Compass, Distil, and Halos API clients."""

import pytest
from adlc_finops.clients import CompassClient, DistilClient, HalosClient
from adlc_finops.models import RolloutRing

def test_compass_client():
    client = CompassClient(mock_mode=True)
    conf = client.configure_session("org/repo", "dev_1", 5.0, ["pytest"])
    assert conf["status"] == "configured"
    assert conf["human_merge_required"] is True

    # Test dangerous command guardrails
    bad_cmd = client.validate_command("rm -rf /")
    assert bad_cmd["allowed"] is False
    assert "blocked" in bad_cmd["reason"].lower()

    good_cmd = client.validate_command("pytest -v")
    assert good_cmd["allowed"] is True

    # Test bounded execution
    task = client.execute_bounded_task("Unit Fix", "org/repo", "Fix typo", 5.0)
    assert task["cost_spent_usd"] <= 5.0

def test_distil_client():
    client = DistilClient(mock_mode=True)
    res = client.compress_context("A" * 1000, mode="lossless")
    assert res["compressed_tokens"] < res["raw_tokens"]
    assert res["recoverable"] is True
    assert res["gross_savings_usd"] > 0

    savings = client.get_savings_report("org/repo")
    assert savings["net_savings_usd"] > 0
    assert savings["roi_ratio"] > 1.0

    audit = client.audit_compressor("lossless-v1")
    assert audit["verdict"] == "PROVEN_SAFE"

def test_halos_client():
    client = HalosClient(mock_mode=True)
    enroll = client.enroll_entity("dev_1:org/repo", "dev_repo", RolloutRing.CANARY_5)
    assert enroll["enrolled"] is True
    assert enroll["assigned_ring"] == "canary_5"

    rel = client.get_latest_signed_release(RolloutRing.CANARY_5)
    assert "signature" in rel
    assert "claude_code" in rel["pinned_cli_versions"]

    gate = client.evaluate_rollout_gate("rel-1", RolloutRing.CANARY_1)
    assert gate["gate_passed"] is True

    kill = client.broadcast_kill_switch(True, "Emergency test")
    assert kill["kill_switch_active"] is True
