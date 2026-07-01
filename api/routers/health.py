"""Health check router."""
from __future__ import annotations
from fastapi import APIRouter
from core.config import settings
from llm.factory import get_provider_display_name
from schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    provider_name, _ = get_provider_display_name()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        provider=provider_name,
    )
