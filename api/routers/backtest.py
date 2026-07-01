"""Backtest / validation router."""
from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException
from schemas.narrative import BacktestRequest, BacktestResponse
from services.validation_service import run_backtest

logger = logging.getLogger(__name__)
router = APIRouter(tags=["backtest"])


@router.post("/backtest", response_model=BacktestResponse)
async def backtest(request: BacktestRequest) -> BacktestResponse:
    try:
        return run_backtest(request)
    except RuntimeError as exc:
        logger.error("Backtest failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error during backtest")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
