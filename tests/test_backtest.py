"""Tests for backtest / validation endpoint."""
from __future__ import annotations


def test_backtest_basic(client, mock_backtest_provider):
    res = client.post("/api/v1/backtest", json={"year": "2024"})
    assert res.status_code == 200
    data = res.json()
    assert "predicted" in data
    assert "actual" in data
    assert "year" in data
    assert data["year"] == "2024"


def test_backtest_custom_question(client, mock_backtest_provider):
    res = client.post("/api/v1/backtest", json={
        "year": "2022",
        "question": "How did EV subsidies change in 2022?",
    })
    assert res.status_code == 200


def test_backtest_all_years(client, mock_backtest_provider):
    for year in ("2021", "2022", "2023", "2024", "2025", "2026"):
        res = client.post("/api/v1/backtest", json={"year": year})
        assert res.status_code == 200, f"Failed for year: {year}"


def test_backtest_meta_present(client, mock_backtest_provider):
    data = client.post("/api/v1/backtest", json={"year": "2023"}).json()
    meta = data["meta"]
    assert "request_id" in meta
    assert "provider" in meta
    assert "latency_ms" in meta


def test_backtest_invalid_year(client):
    res = client.post("/api/v1/backtest", json={"year": "2019"})
    assert res.status_code == 422


def test_backtest_unversioned(client, mock_backtest_provider):
    res = client.post("/api/backtest", json={"year": "2024"})
    assert res.status_code == 200
