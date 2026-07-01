"""Core three-act narrative generation engine."""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any

from core.logging_config import get_logger
from llm.factory import get_llm_provider, get_provider_display_name
from retrieval.retriever import retrieve
from schemas.narrative import (
    NarrativeItem,
    NarrativeMeta,
    NarrativeRequest,
    NarrativeResponse,
    SourceRef,
)

logger = get_logger(__name__)

# ── Scenario descriptions ─────────────────────────────────────────────────────

SCENARIO_DESCRIPTIONS: dict[str, str] = {
    "baseline": (
        "Baseline — Current Market Conditions: The EV market continues its current trajectory "
        "with existing federal incentives (IRA clean vehicle credits), moderate infrastructure "
        "growth, stable gas prices, and OEM electrification roadmaps on track."
    ),
    "ev_subsidies_rollback": (
        "Federal EV Subsidies Roll Back: Federal EV tax credits are eliminated or significantly "
        "reduced. Consumer price sensitivity rises sharply, demand weakens in the mass-market "
        "segment, and OEM EV programmes face revised financial models."
    ),
    "gas_prices_spike": (
        "Gas Prices Spike 20 %: Gasoline prices rise sharply. Consumer urgency to switch to "
        "lower-running-cost vehicles intensifies, EV consideration accelerates, and hybrid/PHEV "
        "options see renewed mainstream interest."
    ),
}

# ── Prompts ───────────────────────────────────────────────────────────────────

_SYSTEM = """You are a senior strategic intelligence analyst at Escalent with deep expertise \
in EV market research and automotive industry dynamics. You produce concise, evidence-grounded \
strategic narratives that help executives make informed decisions. You always return valid JSON."""

_USER = """\
TASK: Generate a structured three-act strategic narrative for the analyst's question.

STRATEGIC QUESTION: {question}

SCENARIO CONTEXT:
{scenario_description}

EVIDENCE FROM EVFORWARD LONGITUDINAL RESEARCH (2020–2026):
{evidence_context}

MARKET SIGNALS AND EXTERNAL EVENTS:
{signals_context}

INSTRUCTIONS:
• Act 1 "Where They Are" — 4 to 6 FACT items grounded directly in the evidence. Each fact must \
cite year and source (e.g. "EVForward 2024 / Purchase Intent").
• Act 2 "Where They Are Heading" — 3 to 4 SIGNAL items (observable trends) and 2 to 3 INFERENCE \
items (logical conclusions). Signals must cite sources.
• Act 3 "Now What" — 3 to 5 RECOMMENDATION items ranked by priority (1 = highest). Each \
recommendation must be specific and actionable for an automotive strategy team.
• Adjust all acts for the scenario context. Where the scenario differs from baseline, note the \
directional impact explicitly.

Your entire response must be a single JSON object in the structure below. Do not include any preamble, explanation, or code fences.
{{
  "act1": [
    {{"type": "FACT", "text": "...", "source": "EVForward YYYY / Section"}}
  ],
  "act2": [
    {{"type": "SIGNAL", "text": "...", "source": "..."}},
    {{"type": "INFERENCE", "text": "..."}}
  ],
  "act3": [
    {{"type": "RECOMMENDATION", "text": "...", "priority": 1}}
  ],
  "sources": [
    {{"id": "ev-YYYY", "title": "EVForward YYYY Core Report", "year": "YYYY", "category": "EVForward Research"}}
  ],
  "confidence": 0.85,
  "narrative_summary": "One-sentence strategic summary of the situation."
}}"""


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt_evidence(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "(No evidence retrieved — run ingestion first)"
    lines = []
    for i, c in enumerate(chunks[:8], 1):
        m = c.get("metadata", {})
        yr, src, sec = m.get("year", "?"), m.get("source", "EVForward"), m.get("section", "")
        label = f"[{yr}][{src}]" + (f"[{sec}]" if sec else "")
        lines.append(f"{i}. {label} {c.get('text', '')[:500]}")
    return "\n".join(lines)


def _fmt_signals(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "(No signals retrieved — run ingestion first)"
    lines = []
    for i, c in enumerate(chunks[:8], 1):
        m = c.get("metadata", {})
        yr, cat, hl = m.get("year", "?"), m.get("category", "Signal"), m.get("headline", "")
        label = f"[{yr}][{cat}]" + (f" {hl}:" if hl else "")
        lines.append(f"{i}. {label} {c.get('text', '')[:400]}")
    return "\n".join(lines)


# ── Builder helpers ───────────────────────────────────────────────────────────

def _build_items(raw: list, valid: set[str]) -> list[NarrativeItem]:
    items = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        t = str(r.get("type", "")).upper()
        if t not in valid:
            continue
        text = str(r.get("text", "")).strip()
        if not text:
            continue
        items.append(NarrativeItem(
            type=t,  # type: ignore[arg-type]
            text=text,
            source=r.get("source"),
            priority=r.get("priority"),
        ))
    return items


def _build_sources(raw: list, retrieved: dict[str, list]) -> list[SourceRef]:
    sources: list[SourceRef] = []
    seen: set[str] = set()

    for s in raw:
        if not isinstance(s, dict):
            continue
        sid = str(s.get("id", "")).strip()
        if not sid or sid in seen:
            continue
        seen.add(sid)
        sources.append(SourceRef(
            id=sid,
            title=str(s.get("title", sid)),
            year=str(s.get("year", "")),
            category=str(s.get("category", "")),
            file_name=s.get("file_name"),
        ))

    # Auto-supplement from retrieval metadata when LLM returned no sources
    if not sources:
        for chunk in retrieved.get("evidence", []):
            yr = chunk.get("metadata", {}).get("year", "")
            sid = f"ev-{yr}"
            if yr and sid not in seen:
                seen.add(sid)
                sources.append(SourceRef(
                    id=sid, title=f"EVForward {yr} Core Report",
                    year=yr, category="EVForward Research",
                ))
        for chunk in retrieved.get("signals", []):
            yr = chunk.get("metadata", {}).get("year", "")
            sid = f"mkt-{yr}"
            if yr and sid not in seen:
                seen.add(sid)
                sources.append(SourceRef(
                    id=sid, title=f"Market Event Bank {yr}",
                    year=yr, category="Market Signals",
                ))
    return sources


# ── Public interface ──────────────────────────────────────────────────────────

def generate_narrative(request: NarrativeRequest) -> NarrativeResponse:
    """Generate and return a three-act strategic narrative."""
    request_id = str(uuid.uuid4())
    t0 = time.monotonic()

    logger.info(
        "Generating narrative  request_id=%s  scenario=%s  q='%s'",
        request_id, request.scenario, request.question[:70],
    )

    retrieved = retrieve(f"{request.question} {request.scenario}")
    scenario_desc = SCENARIO_DESCRIPTIONS.get(
        request.scenario, SCENARIO_DESCRIPTIONS["baseline"]
    )

    prompt = _USER.format(
        question=request.question,
        scenario_description=scenario_desc,
        evidence_context=_fmt_evidence(retrieved["evidence"]),
        signals_context=_fmt_signals(retrieved["signals"]),
    )

    provider = get_llm_provider()
    provider_name, model_name = get_provider_display_name()
    raw = provider.generate_json(prompt, system=_SYSTEM)

    latency_ms = (time.monotonic() - t0) * 1000
    logger.info(
        "Narrative done  request_id=%s  latency=%.0f ms  provider=%s",
        request_id, latency_ms, provider_name,
    )

    act1 = _build_items(raw.get("act1", []), {"FACT"})
    act2 = _build_items(raw.get("act2", []), {"SIGNAL", "INFERENCE"})
    act3 = _build_items(raw.get("act3", []), {"RECOMMENDATION"})
    sources = _build_sources(raw.get("sources", []), retrieved)

    # Graceful degradation when LLM returned empty acts
    if not act1 and not act2 and not act3:
        act1 = [NarrativeItem(
            type="FACT",
            text=(
                "Evidence retrieval returned no results. "
                "Ensure ingestion has been completed (python run.py --ingest-only) "
                "and that your LLM API key is valid."
            ),
        )]
        act3 = [NarrativeItem(
            type="RECOMMENDATION",
            text="Run `python run.py --ingest` to index the knowledge base, then retry.",
            priority=1,
        )]

    return NarrativeResponse(
        question=request.question,
        scenario=request.scenario,
        act1=act1,
        act2=act2,
        act3=act3,
        sources=sources,
        confidence=float(raw.get("confidence", 0.7)),
        narrative_summary=str(raw.get("narrative_summary", "")),
        meta=NarrativeMeta(
            request_id=request_id,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            provider=provider_name,
            model=model_name,
            latency_ms=round(latency_ms, 1),
        ),
    )
