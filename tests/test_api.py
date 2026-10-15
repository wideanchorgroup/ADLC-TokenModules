"""API integration tests for FastAPI application server."""

import pytest
from starlette.testclient import TestClient
from adlc_finops.server import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "compass" in data["integrated_services"]

def test_dashboard_html(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "ADLC FinOps & Governance Control Plane" in res.text

def test_finops_overview_api(client):
    res = client.get("/api/v1/finops/overview")
    assert res.status_code == 200
    data = res.json()
    assert "total_spend_usd" in data
    assert "cost_per_accepted_task" in data

def test_golden_tasks_api(client):
    res = client.get("/api/v1/golden-tasks/catalog")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) > 0

def test_evidence_records_api(client):
    res = client.get("/api/v1/evidence/records")
    assert res.status_code == 200
    records = res.json()
    assert len(records) > 0
