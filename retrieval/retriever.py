"""Semantic retrieval helpers over ChromaDB collections."""
from __future__ import annotations

from typing import Any

from core.config import settings
from core.logging_config import get_logger
from retrieval.chroma_client import get_chroma_collections

logger = get_logger(__name__)


def retrieve(
    query: str,
    top_k: int | None = None,
    year_filter: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Semantically retrieve evidence and signal chunks for *query*.

    Returns ``{"evidence": [...], "signals": [...]}``.
    Each item is ``{"text": str, "metadata": dict}``.
    """
    k = top_k or settings.retrieval_top_k
    ev_col, sig_col = get_chroma_collections()
    where = {"year": year_filter} if year_filter else None

    ev = _query(ev_col, query, k, where)
    sigs = _query(sig_col, query, k, where)

    logger.debug("Retrieved %d evidence + %d signals  query='%s'", len(ev), len(sigs), query[:60])
    return {"evidence": ev, "signals": sigs}


def retrieve_by_year(year: str) -> dict[str, list[dict[str, Any]]]:
    """Return all stored chunks for a given *year* (no semantic ranking)."""
    ev_col, sig_col = get_chroma_collections()
    where = {"year": year}
    ev = _get_all(ev_col, where, limit=20)
    sigs = _get_all(sig_col, where, limit=20)
    return {"evidence": ev, "signals": sigs}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _query(
    collection: Any,
    query: str,
    n: int,
    where: dict | None,
) -> list[dict[str, Any]]:
    try:
        total = collection.count()
        if total == 0:
            return []
        n = min(n, total)
        kw: dict[str, Any] = {
            "query_texts": [query],
            "n_results": n,
            "include": ["documents", "metadatas"],
        }
        if where:
            kw["where"] = where
        result = collection.query(**kw)
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        return [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
    except Exception as exc:
        logger.warning("Collection query failed: %s", exc)
        return []


def _get_all(collection: Any, where: dict, limit: int) -> list[dict[str, Any]]:
    try:
        total = collection.count()
        if total == 0:
            return []
        kw: dict[str, Any] = {
            "limit": min(limit, total),
            "include": ["documents", "metadatas"],
            "where": where,
        }
        result = collection.get(**kw)
        docs = result.get("documents") or []
        metas = result.get("metadatas") or []
        return [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
    except Exception as exc:
        logger.warning("Collection get failed: %s", exc)
        return []
