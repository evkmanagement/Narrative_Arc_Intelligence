"""Parse and serve evidence report summaries from Hackathon Material."""
from __future__ import annotations

import re
from pathlib import Path

from core.config import EVIDENCE_DIR, SIGNALS_DIR
from core.logging_config import get_logger
from schemas.evidence import EvidenceReportsResponse, ReportSummary

logger = get_logger(__name__)


def _year(filename: str) -> str:
    m = re.search(r"20\d{2}", filename)
    return m.group() if m else "0000"


def _count_entries(text: str) -> int:
    bullets = sum(1 for l in text.splitlines() if l.strip().startswith(("•", "-", "*")))
    signals = len(re.findall(r"##\s+SIG-", text))
    return max(bullets, signals, 1)


def _highlights_evforward(text: str, max_n: int = 6) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        s = line.strip().lstrip("•o\t ").strip()
        if (
            35 < len(s) < 240
            and any(ch.isdigit() for ch in s[:60])
        ):
            out.append(s)
        if len(out) >= max_n:
            break
    return out


def _highlights_signals(text: str, max_n: int = 6) -> list[str]:
    out: list[str] = []
    for m in re.finditer(r"\*\*Headline\*\*\s*\n+(.+)", text):
        h = m.group(1).strip()
        if h:
            out.append(h)
        if len(out) >= max_n:
            break
    return out


def get_evidence_reports() -> EvidenceReportsResponse:
    """Aggregate all report summaries from the Hackathon Material directory."""
    reports: list[ReportSummary] = []

    for path in sorted(EVIDENCE_DIR.glob("*.txt")):
        yr = _year(path.name)
        text = path.read_text(encoding="utf-8", errors="replace")
        reports.append(ReportSummary(
            report_id=f"evforward-{yr}",
            title=f"EVForward {yr} Core Report",
            category="EVForward Research",
            year=yr,
            file_name=path.name,
            entry_count=_count_entries(text),
            highlights=_highlights_evforward(text),
            full_content=text,
        ))

    for path in sorted(SIGNALS_DIR.glob("*.txt")):
        yr = _year(path.name)
        text = path.read_text(encoding="utf-8", errors="replace")
        reports.append(ReportSummary(
            report_id=f"market-events-{yr}",
            title=f"Market Event Bank {yr}",
            category="Market Signals",
            year=yr,
            file_name=path.name,
            entry_count=_count_entries(text),
            highlights=_highlights_signals(text),
            full_content=text,
        ))

    logger.info("Evidence reports loaded: %d total", len(reports))
    return EvidenceReportsResponse(reports=reports, total=len(reports))
