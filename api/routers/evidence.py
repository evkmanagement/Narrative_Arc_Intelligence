"""Evidence report router."""
from __future__ import annotations
from fastapi import APIRouter
from schemas.evidence import EvidenceReportsResponse
from services.evidence_service import get_evidence_reports

router = APIRouter(tags=["evidence"])


@router.get("/evidence/reports", response_model=EvidenceReportsResponse)
async def evidence_reports() -> EvidenceReportsResponse:
    return get_evidence_reports()
