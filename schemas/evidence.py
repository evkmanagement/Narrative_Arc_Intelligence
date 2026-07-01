"""Schemas for evidence report endpoints."""
from __future__ import annotations
from pydantic import BaseModel


class ReportSummary(BaseModel):
    report_id: str
    title: str
    category: str
    year: str
    file_name: str
    entry_count: int
    highlights: list[str]
    full_content: str | None = None


class EvidenceReportsResponse(BaseModel):
    reports: list[ReportSummary]
    total: int
