"""Anthropic Claude messages provider."""
from __future__ import annotations

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config import settings
from core.logging_config import get_logger
from llm.base import BaseLLMProvider

logger = get_logger(__name__)


class ClaudeProvider(BaseLLMProvider):
    """Wraps the anthropic Python SDK."""

    def __init__(self) -> None:
        try:
            import anthropic
            self._anthropic = anthropic
        except ImportError as exc:
            raise ImportError("anthropic package is required: pip install anthropic") from exc
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")
        self._client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key,
            timeout=float(settings.llm_timeout_seconds),
        )
        self._model = settings.claude_model
        logger.info("ClaudeProvider ready  model=%s", self._model)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def complete(self, prompt: str, system: str = "") -> str:
        kwargs: dict = {
            "model": self._model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        response = self._client.messages.create(**kwargs)
        return response.content[0].text if response.content else ""
