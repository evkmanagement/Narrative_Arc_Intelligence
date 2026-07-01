"""Google Gemini provider."""
from __future__ import annotations

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config import settings
from core.logging_config import get_logger
from llm.base import BaseLLMProvider

logger = get_logger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Wraps the google-generativeai SDK."""

    def __init__(self) -> None:
        try:
            import google.generativeai as genai
            self._genai = genai
        except ImportError as exc:
            raise ImportError(
                "google-generativeai package is required: pip install google-generativeai"
            ) from exc
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is not configured")
        genai.configure(api_key=settings.google_api_key)
        self._model = genai.GenerativeModel(settings.gemini_model)
        self._model_name = settings.gemini_model
        logger.info("GeminiProvider ready  model=%s", self._model_name)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def complete(self, prompt: str, system: str = "") -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = self._model.generate_content(
            full_prompt,
            generation_config={"temperature": 0.3, "max_output_tokens": 2048},
        )
        return response.text or ""
