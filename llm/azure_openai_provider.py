"""Azure OpenAI deployment provider."""
from __future__ import annotations

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config import settings
from core.logging_config import get_logger
from llm.base import BaseLLMProvider

logger = get_logger(__name__)


class AzureOpenAIProvider(BaseLLMProvider):
    """Wraps openai.AzureOpenAI for Azure-hosted deployments."""

    def __init__(self) -> None:
        try:
            from openai import AzureOpenAI
        except ImportError as exc:
            raise ImportError("openai package is required: pip install openai") from exc
        if not settings.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not configured")
        if not settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")
        self._client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            timeout=float(settings.llm_timeout_seconds),
        )
        self._deployment = settings.azure_openai_deployment
        logger.info("AzureOpenAIProvider ready  deployment=%s", self._deployment)

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
            model=self._deployment,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
        return response.choices[0].message.content or ""
