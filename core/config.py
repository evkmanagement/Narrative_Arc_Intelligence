"""Application configuration — loaded from environment / .env file."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings

_BASE_DIR: Path = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """All runtime configuration.  Values are read from the process environment
    and/or a ``.env`` file at the project root."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False,
    }

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "What Next Engine"
    app_version: str = "1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # ── LLM ──────────────────────────────────────────────────────────────────
    llm_provider: Literal["azure_openai", "openai", "claude", "gemini"] = "openai"
    llm_timeout_seconds: int = 30
    llm_max_retries: int = 3

    @field_validator("llm_provider", mode="before")
    @classmethod
    def _normalise_provider(cls, v: object) -> str:
        """Accept both hyphenated (azure-openai) and underscored (azure_openai) forms."""
        return str(v).strip().lower().replace("-", "_")

    # Azure OpenAI
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-02-01"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Anthropic
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"

    # Google / Gemini  (accept both GOOGLE_API_KEY and GEMINI_API_KEY)
    google_api_key: str = ""
    gemini_api_key: str = ""   # alias accepted from env: GEMINI_API_KEY
    gemini_model: str = "gemini-1.5-pro"

    @field_validator("google_api_key", mode="after")
    @classmethod
    def _merge_gemini_key(cls, v: str, info) -> str:
        """Fall back to GEMINI_API_KEY if GOOGLE_API_KEY is not set."""
        if not v:
            return info.data.get("gemini_api_key", "")
        return v

    # ── Retrieval ─────────────────────────────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_evidence_collection: str = "evidence_bank"
    chroma_events_collection: str = "market_events"
    retrieval_top_k: int = 8


settings = Settings()

# ── Derived path constants (not environment-sourced) ─────────────────────────
BASE_DIR: Path = _BASE_DIR
KNOWLEDGE_DIR: Path = _BASE_DIR / "knowledge"
CHROMA_DIR: Path = _BASE_DIR / "chroma_db"
HACKATHON_DIR: Path = _BASE_DIR / "Hackathon Material"
EVIDENCE_DIR: Path = HACKATHON_DIR / "Extracted Facts from EVForward Reports"
SIGNALS_DIR: Path = HACKATHON_DIR / "Extrernal Market Signals"
LOGS_DIR: Path = _BASE_DIR / "logs"
