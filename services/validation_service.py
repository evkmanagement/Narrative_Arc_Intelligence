"""Backtest / validation service — predicted vs actual year comparison."""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

from core.logging_config import get_logger
from llm.factory import get_llm_provider, get_provider_display_name
from retrieval.retriever import retrieve, retrieve_by_year
from schemas.narrative import BacktestItem, BacktestRequest, BacktestResponse, NarrativeMeta

logger = get_logger(__name__)

_SYSTEM = "You are a strategic EV market analyst performing a retrospective analysis."

_USER = """\
TASK: Retrospective analysis for the year {year}.

STRATEGIC QUESTION: {question}

PRIOR-YEAR EVIDENCE (years before {year}):
{prior_context}

ACTUAL {year} EVIDENCE:
{actual_context}

Generate a JSON response with:
1. "predicted" — 3–5 items: what prior data would have suggested for {year}
2. "actual" — 3–5 items: what actually happened in {year} per the evidence
3. "accuracy_note" — 1–2 sentence comparison of alignment between predicted and actual

Your entire response must be a single JSON object in the structure below. Do not include any preamble, explanation, or code fences.
{{
  "predicted": [
    {{"label": "Prediction", "text": "...", "source": "Prior years evidence"}}
  ],
  "actual": [
    {{"label": "Actual Outcome", "text": "...", "source": "EVForward {year}"}}
  ],
  "accuracy_note": "..."
}}"""


def _fmt(chunks: list[dict]) -> str:
    if not chunks:
        return "(none available)"
    parts = []
    for c in chunks[:6]:
        m = c.get("metadata", {})
        parts.append(f"[{m.get('year','?')}][{m.get('source','?')}] {c.get('text','')[:400]}")
    return "\n".join(parts)


def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """Run retrospective analysis comparing model prediction to actual outcomes."""
    request_id = str(uuid.uuid4())
    t0 = time.monotonic()
    year = request.year

    logger.info("Backtest start  year=%s  request_id=%s", year, request_id)

    # Prior-year context
    prior = retrieve(f"{request.question} EV adoption trends barriers")
    prior_ev = [c for c in prior["evidence"] if int(c.get("metadata", {}).get("year", "9999")) < int(year)][:6]
    prior_sigs = [c for c in prior["signals"] if int(c.get("metadata", {}).get("year", "9999")) < int(year)][:6]
    prior_context = _fmt(prior_ev + prior_sigs)

    # Actual year context
    actual = retrieve_by_year(year)
    actual_context = _fmt(actual["evidence"] + actual["signals"])

    prompt = _USER.format(
        year=year,
        question=request.question,
        prior_context=prior_context,
        actual_context=actual_context,
    )

    provider = get_llm_provider()
    provider_name, model_name = get_provider_display_name()
    raw = provider.generate_json(prompt, system=_SYSTEM)

    latency_ms = (time.monotonic() - t0) * 1000

    def _items(lst: list) -> list[BacktestItem]:
        out = []
        for r in lst:
            if not isinstance(r, dict):
                continue
            t = str(r.get("text", "")).strip()
            if t:
                out.append(BacktestItem(label=str(r.get("label", "Item")), text=t, source=r.get("source")))
        return out

    predicted = _items(raw.get("predicted", []))
    actual_items = _items(raw.get("actual", []))

    if not predicted:
        predicted = [BacktestItem(label="Prediction", text="Insufficient prior data to generate prediction.")]
    if not actual_items:
        actual_items = [BacktestItem(label="Actual", text=f"No {year} data found in knowledge base.")]

    logger.info("Backtest done  year=%s  latency=%.0f ms", year, latency_ms)

    return BacktestResponse(
        year=year,
        question=request.question,
        predicted=predicted,
        actual=actual_items,
        accuracy_note=str(raw.get("accuracy_note", "")),
        meta=NarrativeMeta(
            request_id=request_id,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            provider=provider_name,
            model=model_name,
            latency_ms=round(latency_ms, 1),
        ),
    )
