"""ChromaDB persistent client singleton."""
from __future__ import annotations

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from core.config import CHROMA_DIR, settings
from core.logging_config import get_logger

logger = get_logger(__name__)

_client: chromadb.ClientAPI | None = None
_embedding_fn: SentenceTransformerEmbeddingFunction | None = None


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        logger.info("ChromaDB client initialised at %s", CHROMA_DIR)
    return _client


def _get_embedding_fn() -> SentenceTransformerEmbeddingFunction:
    global _embedding_fn
    if _embedding_fn is None:
        logger.info("Loading embedding model: %s", settings.embedding_model)
        _embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )
        logger.info("Embedding model loaded")
    return _embedding_fn


def get_chroma_collections() -> tuple[chromadb.Collection, chromadb.Collection]:
    """Return (evidence_collection, market_events_collection)."""
    client = _get_client()
    ef = _get_embedding_fn()
    evidence_col = client.get_or_create_collection(
        name=settings.chroma_evidence_collection,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    events_col = client.get_or_create_collection(
        name=settings.chroma_events_collection,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return evidence_col, events_col
