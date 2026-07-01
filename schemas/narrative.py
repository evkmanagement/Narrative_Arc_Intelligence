"""Schemas for narrative generation and backtest."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ── Request ───────────────────────────────────────────────────────────────────

class NarrativeRequest(BaseModel):
    question: str = Field(..., min_length=10, max_length=500)
    scenario: Literal["baseline", "ev_subsidies_rollback", "gas_prices_spike"] = "baseline"


class BacktestRequest(BaseModel):
    year: Literal["2021", "2022", "2023", "2024", "2025", "2026"]
    question: str = Field(
        default="What were the key EV market developments and adoption trends?",
        min_length=10,
        max_length=500,
    )


# ── Response building blocks ──────────────────────────────────────────────────

class NarrativeItem(BaseModel):
    type: Literal["FACT", "SIGNAL", "INFERENCE", "RECOMMENDATION"]
    text: str
    source: str | None = None
    priority: int | None = None


class SourceRef(BaseModel):
    id: str
    title: str
    year: str
    category: str
    file_name: str | None = None


class NarrativeMeta(BaseModel):
    request_id: str
    generated_at_utc: str
    provider: str
    model: str
    latency_ms: float


# ── Narrative response ────────────────────────────────────────────────────────

class NarrativeResponse(BaseModel):
    question: str
    scenario: str
    act1: list[NarrativeItem]
    act2: list[NarrativeItem]
    act3: list[NarrativeItem]
    sources: list[SourceRef]
    confidence: float = 0.0
    narrative_summary: str = ""
    meta: NarrativeMeta


# ── Backtest response ─────────────────────────────────────────────────────────

class BacktestItem(BaseModel):
    label: str
    text: str
    source: str | None = None


class BacktestResponse(BaseModel):
    year: str
    question: str
    predicted: list[BacktestItem]
    actual: list[BacktestItem]
    accuracy_note: str
    meta: NarrativeMeta
