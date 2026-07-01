"""PDF export router."""
from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from schemas.narrative import NarrativeRequest
from services.narrative_engine import generate_narrative
from services.pdf_service import generate_pdf

logger = logging.getLogger(__name__)
router = APIRouter(tags=["export"])


@router.post("/export/pdf")
async def export_pdf(request: NarrativeRequest) -> Response:
    """Generate narrative and return as a branded PDF download."""
    try:
        narrative = generate_narrative(request)
        pdf_bytes = generate_pdf(narrative)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="what_next_engine_report.pdf"'},
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("PDF export failed")
        raise HTTPException(status_code=500, detail="PDF export failed") from exc
