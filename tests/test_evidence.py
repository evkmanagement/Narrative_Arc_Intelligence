"""Tests for evidence reports endpoint and service."""
from __future__ import annotations

import pytest


def test_evidence_reports_endpoint(client):
    res = client.get("/api/v1/evidence/reports")
    assert res.status_code == 200
    data = res.json()
    assert "reports" in data
    assert "total" in data
    assert data["total"] == len(data["reports"])


def test_evidence_reports_count(client):
    """Expect 14 reports: 7 EVForward + 7 Market Event Bank."""
    data = client.get("/api/v1/evidence/reports").json()
    assert data["total"] >= 14


def test_evidence_report_schema(client):
    reports = client.get("/api/v1/evidence/reports").json()["reports"]
    required = {"report_id", "title", "category", "year", "file_name", "entry_count", "highlights"}
    for report in reports[:3]:
        assert required.issubset(report.keys()), f"Missing keys in {report.get('report_id')}"


def test_evidence_report_categories(client):
    reports = client.get("/api/v1/evidence/reports").json()["reports"]
    categories = {r["category"] for r in reports}
    assert "EVForward Research" in categories
    assert "Market Signals" in categories


def test_evidence_report_years_coverage(client):
    reports = client.get("/api/v1/evidence/reports").json()["reports"]
    years = {r["year"] for r in reports}
    for expected_year in ("2020", "2021", "2022", "2023", "2024", "2025", "2026"):
        assert expected_year in years, f"Missing year {expected_year} in evidence reports"


def test_evidence_report_highlights_non_empty(client):
    reports = client.get("/api/v1/evidence/reports").json()["reports"]
    for r in reports:
        assert isinstance(r["highlights"], list)


def test_evidence_service_direct():
    from services.evidence_service import get_evidence_reports
    result = get_evidence_reports()
    assert result.total > 0
    assert len(result.reports) == result.total
    for report in result.reports:
        assert report.year.isdigit()
        assert len(report.year) == 4
