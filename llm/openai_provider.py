"""OpenAI GPT chat-completions provider."""
from __future__ import annotations

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config import settings
from core.logging_config import get_logger
from llm.base import BaseLLMProvider

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """Wraps the openai Python SDK for GPT models."""

    def __init__(self) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("openai package is required: pip install openai") from exc
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        self._client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=float(settings.llm_timeout_seconds),
        )
        self._model = settings.openai_model
        logger.info("OpenAIProvider ready  model=%s", self._model)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def complete(self, prompt: str, system: str = "") -> str:
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
        return response.choices[0].message.content or ""
