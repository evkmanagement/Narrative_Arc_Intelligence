"""LLM provider factory with automatic fallback."""
from __future__ import annotations

from core.config import settings
from core.logging_config import get_logger
from llm.base import BaseLLMProvider

logger = get_logger(__name__)

_PROVIDER_ORDER = ["azure_openai", "openai", "claude", "gemini"]


def _build_provider(name: str) -> BaseLLMProvider:
    if name == "azure_openai":
        from llm.azure_openai_provider import AzureOpenAIProvider
        return AzureOpenAIProvider()
    if name == "openai":
        from llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    if name == "claude":
        from llm.claude_provider import ClaudeProvider
        return ClaudeProvider()
    if name == "gemini":
        from llm.gemini_provider import GeminiProvider
        return GeminiProvider()
    raise ValueError(f"Unknown LLM provider: {name}")


def get_llm_provider() -> BaseLLMProvider:
    """Return the configured provider, falling back to alternates on config failure."""
    preferred = settings.llm_provider
    candidates = [preferred] + [p for p in _PROVIDER_ORDER if p != preferred]

    last_error: Exception | None = None
    for name in candidates:
        try:
            provider = _build_provider(name)
            if name != preferred:
                logger.warning("Fell back to LLM provider=%s (preferred=%s failed)", name, preferred)
            else:
                logger.info("Using LLM provider=%s", name)
            return provider
        except (ValueError, ImportError) as exc:
            logger.debug("Provider %s unavailable: %s", name, exc)
            last_error = exc

    raise RuntimeError(
        f"No LLM provider could be initialised. Last error: {last_error}"
    )


def get_provider_display_name() -> tuple[str, str]:
    """Return (provider_label, model_name) for display / logging."""
    p = settings.llm_provider
    if p == "azure_openai":
        return "Azure OpenAI", settings.azure_openai_deployment
    if p == "openai":
        return "OpenAI", settings.openai_model
    if p == "claude":
        return "Anthropic Claude", settings.claude_model
    if p == "gemini":
        return "Google Gemini", settings.gemini_model
    return p, "unknown"
