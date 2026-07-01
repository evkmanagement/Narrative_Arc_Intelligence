"""Tests for health endpoints."""
from __future__ import annotations


def test_health_unversioned(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "provider" in data


def test_health_versioned(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


def test_health_response_fields(client):
    data = client.get("/api/v1/health").json()
    assert set(data.keys()) >= {"status", "version", "provider"}
