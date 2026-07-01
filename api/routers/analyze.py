"""Narrative analysis router."""
from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException
from schemas.narrative import NarrativeRequest, NarrativeResponse
from services.narrative_engine import generate_narrative

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=NarrativeResponse)
async def analyze(request: NarrativeRequest) -> NarrativeResponse:
    try:
        return generate_narrative(request)
    except RuntimeError as exc:
        logger.error("Narrative generation failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error during narrative generation")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
