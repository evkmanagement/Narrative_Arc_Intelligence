"""Structured logging: console + run.log at project root."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

_RUN_LOG = Path(__file__).resolve().parent.parent / "run.log"
_FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"

_configured = False


def setup_logging(log_level: str = "INFO") -> None:
    """Configure root logger with console + file handlers (idempotent)."""
    global _configured
    if _configured:
        return
    _configured = True

    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root.handlers.clear()

    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    fh = logging.FileHandler(_RUN_LOG, encoding="utf-8")
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # Quiet noisy libraries
    for noisy in ("uvicorn.access", "chromadb", "sentence_transformers", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
