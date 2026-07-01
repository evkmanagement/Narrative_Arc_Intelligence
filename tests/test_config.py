"""Tests for config and scenario endpoints."""
from __future__ import annotations


def test_config_unversioned(client):
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data
    assert "model" in data
    assert "retrieval_top_k" in data
    assert isinstance(data["collections"], list)


def test_config_versioned(client):
    res = client.get("/api/v1/config")
    assert res.status_code == 200


def test_scenarios_unversioned(client):
    res = client.get("/api/scenarios")
    assert res.status_code == 200
    data = res.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) == 3


def test_scenarios_versioned(client):
    res = client.get("/api/v1/scenarios")
    assert res.status_code == 200
    ids = [s["id"] for s in res.json()["scenarios"]]
    assert "baseline" in ids
    assert "ev_subsidies_rollback" in ids
    assert "gas_prices_spike" in ids


def test_scenarios_have_required_fields(client):
    scenarios = client.get("/api/v1/scenarios").json()["scenarios"]
    for s in scenarios:
        assert "id" in s
        assert "label" in s
        assert "description" in s
