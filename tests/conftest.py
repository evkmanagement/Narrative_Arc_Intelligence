"""Shared pytest fixtures and helpers."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

# Ensure project root is on the path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ── Mock LLM Provider ─────────────────────────────────────────────────────────

class MockLLMProvider:
    """Returns a pre-configured JSON payload without calling any external API."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def complete(self, prompt: str, system: str = "") -> str:
        return json.dumps(self._payload)

    def generate_json(self, prompt: str, system: str = "") -> dict[str, Any]:
        return self._payload


# ── Standard mock narrative payload ──────────────────────────────────────────

MOCK_NARRATIVE_PAYLOAD: dict[str, Any] = {
    "act1": [
        {"type": "FACT", "text": "BEV purchase intent score is 38 in 2024.", "source": "EVForward 2024"},
        {"type": "FACT", "text": "8% of new-vehicle buyers own a BEV as of 2024.", "source": "EVForward 2024"},
    ],
    "act2": [
        {"type": "SIGNAL", "text": "EV adoption is accelerating across all income segments.", "source": "EVForward 2024"},
        {"type": "INFERENCE", "text": "Mass market EV adoption is approaching an inflection point."},
    ],
    "act3": [
        {"type": "RECOMMENDATION", "text": "Expand public fast-charging coverage on major highway corridors.", "priority": 1},
        {"type": "RECOMMENDATION", "text": "Target Dreamer and Pragmatist personas with targeted messaging.", "priority": 2},
    ],
    "sources": [
        {"id": "ev-2024", "title": "EVForward 2024 Core Report", "year": "2024", "category": "EVForward Research"},
        {"id": "mkt-2024", "title": "Market Event Bank 2024", "year": "2024", "category": "Market Signals"},
    ],
    "confidence": 0.85,
    "narrative_summary": "EV adoption is accelerating but infrastructure and cost barriers persist.",
}

MOCK_BACKTEST_PAYLOAD: dict[str, Any] = {
    "predicted": [
        {"label": "Prediction", "text": "BEV intent would reach ~35% by 2024.", "source": "Prior years evidence"},
    ],
    "actual": [
        {"label": "Actual Outcome", "text": "BEV purchase intent score reached 38 in 2024.", "source": "EVForward 2024"},
    ],
    "accuracy_note": "Prediction was directionally correct; actual intent slightly exceeded forecast.",
}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient (session-scoped for speed)."""
    from api.main import app
    return TestClient(app)


@pytest.fixture
def mock_narrative_provider(monkeypatch):
    """Patch narrative engine to use MockLLMProvider."""
    import services.narrative_engine as engine
    monkeypatch.setattr(engine, "get_llm_provider", lambda: MockLLMProvider(MOCK_NARRATIVE_PAYLOAD))
    return MockLLMProvider(MOCK_NARRATIVE_PAYLOAD)


@pytest.fixture
def mock_backtest_provider(monkeypatch):
    """Patch validation service to use MockLLMProvider."""
    import services.validation_service as svc
    monkeypatch.setattr(svc, "get_llm_provider", lambda: MockLLMProvider(MOCK_BACKTEST_PAYLOAD))
    return MockLLMProvider(MOCK_BACKTEST_PAYLOAD)


@pytest.fixture
def mock_pdf_provider(monkeypatch):
    """Patch pdf service's narrative engine to avoid real LLM calls."""
    import services.narrative_engine as engine
    monkeypatch.setattr(engine, "get_llm_provider", lambda: MockLLMProvider(MOCK_NARRATIVE_PAYLOAD))
