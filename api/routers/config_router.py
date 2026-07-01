"""Configuration router."""
from __future__ import annotations
from fastapi import APIRouter
from core.config import settings
from llm.factory import get_provider_display_name
from schemas.common import ConfigResponse

router = APIRouter(tags=["config"])


@router.get("/config", response_model=ConfigResponse)
async def config() -> ConfigResponse:
    provider_name, model_name = get_provider_display_name()
    return ConfigResponse(
        provider=provider_name,
        model=model_name,
        retrieval_top_k=settings.retrieval_top_k,
        collections=[
            settings.chroma_evidence_collection,
            settings.chroma_events_collection,
        ],
        version=settings.app_version,
    )
