"""Full ingestion pipeline: parse → knowledge files → ChromaDB."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from core.config import EVIDENCE_DIR, KNOWLEDGE_DIR, SIGNALS_DIR
from core.logging_config import get_logger

logger = get_logger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_year(filename: str) -> str:
    m = re.search(r"20\d{2}", filename)
    return m.group() if m else "0000"


def _make_id(*parts: str) -> str:
    return hashlib.md5("".join(parts).encode()).hexdigest()


# ── EVForward evidence parser ─────────────────────────────────────────────────

def _parse_evforward_file(path: Path) -> list[dict[str, Any]]:
    """Parse an EVForward evidence .txt into section-level chunk records."""
    text = path.read_text(encoding="utf-8", errors="replace")
    year = _extract_year(path.name)
    chunks: list[dict[str, Any]] = []
    current_section = "General"
    buffer: list[str] = []

    section_header_re = re.compile(
        r"^(?:\d+\.\s+)?[A-Z][A-Za-z &/()&–-]{3,}[:\s]*$"
    )

    def flush() -> None:
        lines = [
            ln.strip().lstrip("•o\t ").strip()
            for ln in buffer
            if ln.strip() and "___" not in ln
        ]
        combined = " ".join(lines)
        if len(combined) > 40:
            cid = _make_id(year, current_section, combined[:40])
            chunks.append({
                "id": cid,
                "text": combined[:2000],
                "year": year,
                "section": current_section,
                "source": f"EVForward {year}",
                "category": "EVForward Research",
                "file_name": path.name,
            })
        buffer.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if section_header_re.match(stripped) and len(stripped) < 80:
            if buffer:
                flush()
            current_section = stripped.rstrip(":").strip()
        else:
            buffer.append(line)

    if buffer:
        flush()

    # Always keep at least one chunk per file
    if not chunks:
        cid = _make_id(year, path.name)
        chunks.append({
            "id": cid,
            "text": text[:3000],
            "year": year,
            "section": "Full Report",
            "source": f"EVForward {year}",
            "category": "EVForward Research",
            "file_name": path.name,
        })

    logger.debug("EVForward %s → %d chunks", path.name, len(chunks))
    return chunks


# ── Market Event Bank parser ──────────────────────────────────────────────────

def _parse_market_events_file(path: Path) -> list[dict[str, Any]]:
    """Parse a Market Event Bank .txt into per-signal chunk records."""
    text = path.read_text(encoding="utf-8", errors="replace")
    year = _extract_year(path.name)
    chunks: list[dict[str, Any]] = []

    # Split on ## SIG- headers
    blocks = re.split(r"\n(?=##\s+SIG-)", text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        sig_match = re.search(r"##\s+(SIG-[A-Z]+-\d{4}-\d+)", block)
        sig_id = sig_match.group(1) if sig_match else f"SIG-UNK-{year}"

        headline_match = re.search(r"\*\*Headline\*\*\s*\n+(.+)", block)
        headline = headline_match.group(1).strip() if headline_match else ""

        category_match = re.search(r"\*\*Category\*\*\s*\n+(.+)", block)
        category = category_match.group(1).strip() if category_match else "Unknown"

        obs_match = re.search(
            r"\*\*Observed Change\*\*\s*\n+(.*?)(?=\n\*\*[A-Z]|\Z)", block, re.DOTALL
        )
        observed = obs_match.group(1).strip() if obs_match else ""
        observed = re.sub(r"\[web:\d+\]", "", observed).strip()

        combined = " ".join(filter(None, [headline, observed]))[:1500]
        if len(combined) < 15:
            combined = block[:500]

        cid = _make_id(sig_id, combined[:40])
        chunks.append({
            "id": cid,
            "text": combined,
            "year": year,
            "signal_id": sig_id,
            "headline": headline,
            "category": category,
            "source": f"Market Events {year}",
            "source_category": "Market Signals",
            "file_name": path.name,
        })

    logger.debug("Market Events %s → %d chunks", path.name, len(chunks))
    return chunks


# ── Knowledge file writers ────────────────────────────────────────────────────

def _write_knowledge_files(
    ev_chunks: list[dict[str, Any]],
    sig_chunks: list[dict[str, Any]],
) -> None:
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    ev_path = KNOWLEDGE_DIR / "evidence_bank.txt"
    ms_path = KNOWLEDGE_DIR / "market_events.txt"

    with ev_path.open("w", encoding="utf-8") as fh:
        for c in ev_chunks:
            fh.write(
                f"[YEAR:{c['year']}] [SOURCE:{c['source']}] [SECTION:{c['section']}]\n"
                f"{c['text']}\n---\n"
            )

    with ms_path.open("w", encoding="utf-8") as fh:
        for c in sig_chunks:
            fh.write(
                f"[YEAR:{c['year']}] [ID:{c['signal_id']}] [CAT:{c['category']}]\n"
                f"{c['text']}\n---\n"
            )

    logger.info("Knowledge files written: %s, %s", ev_path, ms_path)


# ── ChromaDB indexing ─────────────────────────────────────────────────────────

def _upsert_batch(collection: Any, chunks: list[dict[str, Any]], batch: int = 100) -> None:
    ids, texts, metas = [], [], []
    for c in chunks:
        ids.append(c["id"])
        texts.append(c["text"])
        metas.append({k: str(v) for k, v in c.items() if k not in ("id", "text")})
    for i in range(0, len(ids), batch):
        collection.upsert(
            ids=ids[i : i + batch],
            documents=texts[i : i + batch],
            metadatas=metas[i : i + batch],
        )


def _index_to_chroma(
    ev_chunks: list[dict[str, Any]],
    sig_chunks: list[dict[str, Any]],
) -> None:
    from retrieval.chroma_client import get_chroma_collections

    ev_col, sig_col = get_chroma_collections()
    if ev_chunks:
        _upsert_batch(ev_col, ev_chunks)
        logger.info("ChromaDB: indexed %d evidence chunks", len(ev_chunks))
    if sig_chunks:
        _upsert_batch(sig_col, sig_chunks)
        logger.info("ChromaDB: indexed %d signal chunks", len(sig_chunks))


# ── Public interface ──────────────────────────────────────────────────────────

def run_ingestion(force: bool = False) -> dict[str, int]:
    """
    Parse Hackathon Material, write knowledge files, and index into ChromaDB.

    Pass ``force=True`` to re-index even when knowledge files already exist.
    Returns ``{"evidence": N, "signals": N}``.
    """
    ev_path = KNOWLEDGE_DIR / "evidence_bank.txt"
    ms_path = KNOWLEDGE_DIR / "market_events.txt"

    if not force and ev_path.exists() and ms_path.exists():
        logger.info("Knowledge files exist — skipping ingestion (pass force=True to re-index)")
        ev_count = ev_path.read_text(encoding="utf-8", errors="replace").count("\n---\n")
        ms_count = ms_path.read_text(encoding="utf-8", errors="replace").count("\n---\n")
        return {"evidence": ev_count, "signals": ms_count}

    logger.info("Starting ingestion pipeline…")

    ev_chunks: list[dict[str, Any]] = []
    for f in sorted(EVIDENCE_DIR.glob("*.txt")):
        ev_chunks.extend(_parse_evforward_file(f))

    sig_chunks: list[dict[str, Any]] = []
    for f in sorted(SIGNALS_DIR.glob("*.txt")):
        sig_chunks.extend(_parse_market_events_file(f))

    logger.info(
        "Parsed %d evidence + %d signal chunks", len(ev_chunks), len(sig_chunks)
    )

    _write_knowledge_files(ev_chunks, sig_chunks)
    _index_to_chroma(ev_chunks, sig_chunks)

    logger.info("Ingestion pipeline complete.")
    return {"evidence": len(ev_chunks), "signals": len(sig_chunks)}
