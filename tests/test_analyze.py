"""Tests for the /analyze endpoints (LLM calls are mocked)."""
from __future__ import annotations


def test_analyze_baseline(client, mock_narrative_provider):
    res = client.post("/api/v1/analyze", json={
        "question": "What are the primary barriers to EV adoption today?",
        "scenario": "baseline",
    })
    assert res.status_code == 200
    data = res.json()
    assert "act1" in data
    assert "act2" in data
    assert "act3" in data
    assert "sources" in data
    assert "meta" in data


def test_analyze_scenario_variants(client, mock_narrative_provider):
    for scenario in ("baseline", "ev_subsidies_rollback", "gas_prices_spike"):
        res = client.post("/api/v1/analyze", json={
            "question": "How will EV market evolve given policy shifts?",
            "scenario": scenario,
        })
        assert res.status_code == 200, f"Failed for scenario: {scenario}"


def test_analyze_meta_fields(client, mock_narrative_provider):
    res = client.post("/api/v1/analyze", json={
        "question": "What trends define the EV landscape in 2024?",
        "scenario": "baseline",
    })
    meta = res.json()["meta"]
    assert "request_id" in meta
    assert "provider" in meta
    assert "latency_ms" in meta
    assert "generated_at_utc" in meta


def test_analyze_act1_items_are_facts(client, mock_narrative_provider):
    data = client.post("/api/v1/analyze", json={
        "question": "Describe key EV ownership barriers in detail?",
        "scenario": "baseline",
    }).json()
    for item in data["act1"]:
        assert item["type"] == "FACT"


def test_analyze_act2_item_types(client, mock_narrative_provider):
    data = client.post("/api/v1/analyze", json={
        "question": "What signals indicate EV momentum in the market?",
        "scenario": "baseline",
    }).json()
    valid_types = {"SIGNAL", "INFERENCE"}
    for item in data["act2"]:
        assert item["type"] in valid_types


def test_analyze_act3_are_recommendations(client, mock_narrative_provider):
    data = client.post("/api/v1/analyze", json={
        "question": "What should automotive brands do to drive EV adoption?",
        "scenario": "baseline",
    }).json()
    for item in data["act3"]:
        assert item["type"] == "RECOMMENDATION"


def test_analyze_question_too_short(client):
    res = client.post("/api/v1/analyze", json={"question": "Too short", "scenario": "baseline"})
    assert res.status_code == 422


def test_analyze_question_too_long(client):
    res = client.post("/api/v1/analyze", json={"question": "x" * 501, "scenario": "baseline"})
    assert res.status_code == 422


def test_analyze_invalid_scenario(client):
    res = client.post("/api/v1/analyze", json={
        "question": "Valid question that is long enough to pass validation?",
        "scenario": "invalid_scenario",
    })
    assert res.status_code == 422


def test_analyze_unversioned_also_works(client, mock_narrative_provider):
    res = client.post("/api/analyze", json={
        "question": "How do gas price spikes affect EV adoption rates?",
        "scenario": "gas_prices_spike",
    })
    assert res.status_code == 200
