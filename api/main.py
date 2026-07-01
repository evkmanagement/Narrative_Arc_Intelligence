"""FastAPI application factory."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from core.config import BASE_DIR, settings
from core.logging_config import setup_logging

setup_logging("DEBUG" if settings.debug else "INFO")
logger = logging.getLogger(__name__)

_FRONTEND = BASE_DIR / "frontend"


@asynccontextmanager
async def _lifespan(app: FastAPI):
    logger.info("=== What Next Engine v%s starting ===", settings.app_version)
    logger.info("Provider: %s  Debug: %s", settings.llm_provider, settings.debug)
    try:
        from retrieval.chroma_client import get_chroma_collections
        get_chroma_collections()
        logger.info("ChromaDB collections ready")
    except Exception as exc:
        logger.warning("ChromaDB warm-up skipped: %s", exc)
    yield
    logger.info("=== What Next Engine shutdown ===")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "What Next Engine — Evidence-grounded strategic intelligence "
            "for EV market decisions. Powered by Escalent EVForward data."
        ),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=_lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    from api.routers import (
        analyze,
        backtest,
        config_router,
        evidence,
        export,
        health,
        scenarios,
    )

    for prefix in ("/api", "/api/v1"):
        app.include_router(health.router, prefix=prefix)
        app.include_router(config_router.router, prefix=prefix)
        app.include_router(scenarios.router, prefix=prefix)
        app.include_router(analyze.router, prefix=prefix)
        app.include_router(backtest.router, prefix=prefix)

    # Evidence and export only on v1 / base
    app.include_router(evidence.router, prefix="/api/v1")
    app.include_router(export.router, prefix="/api")

    # ── Static assets ─────────────────────────────────────────────────────────
    css_dir = _FRONTEND / "css"
    js_dir = _FRONTEND / "js"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

    # ── Serve frontend ────────────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        idx = _FRONTEND / "index.html"
        if idx.exists():
            return FileResponse(str(idx))
        return {"message": "Frontend not found. API is available at /api/docs"}

    return app


app = create_app()
