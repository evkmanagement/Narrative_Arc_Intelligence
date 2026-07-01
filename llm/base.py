"""Abstract base class for all LLM providers."""
from __future__ import annotations

import abc
import json
import re
from typing import Any

from core.logging_config import get_logger

logger = get_logger(__name__)


class BaseLLMProvider(abc.ABC):
    """Every LLM backend must implement this interface."""

    @abc.abstractmethod
    def complete(self, prompt: str, system: str = "") -> str:
        """Send a prompt and return raw text."""

    def generate_json(self, prompt: str, system: str = "") -> dict[str, Any]:
        """Call ``complete`` and parse the result as JSON with repair fallback."""
        raw = self.complete(prompt, system=system)
        return self._parse_json(raw)

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        """Extract a JSON object from a raw LLM response string."""
        # Strip markdown fences
        cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()

        # Direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Find the outermost {...} block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        logger.warning("JSON parse failed; returning empty scaffold")
        return {
            "act1": [],
            "act2": [],
            "act3": [],
            "sources": [],
            "confidence": 0.0,
            "narrative_summary": "Narrative generation encountered a parsing error.",
        }
