"""Tests for PDF export endpoint."""
from __future__ import annotations


def test_pdf_export_returns_pdf(client, mock_pdf_provider):
    res = client.post("/api/export/pdf", json={
        "question": "What are the key drivers of EV adoption in the current market?",
        "scenario": "baseline",
    })
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000  # Should be a real PDF


def test_pdf_export_content_disposition(client, mock_pdf_provider):
    res = client.post("/api/export/pdf", json={
        "question": "How will EV subsidies rollback affect demand patterns?",
        "scenario": "ev_subsidies_rollback",
    })
    assert "attachment" in res.headers.get("content-disposition", "")
    assert ".pdf" in res.headers.get("content-disposition", "")


def test_pdf_starts_with_pdf_header(client, mock_pdf_provider):
    res = client.post("/api/export/pdf", json={
        "question": "What infrastructure gaps need addressing for mass EV adoption?",
        "scenario": "gas_prices_spike",
    })
    # PDF files start with %PDF
    assert res.content[:4] == b"%PDF"


def test_pdf_service_directly():
    """Test PDF generation directly without HTTP layer."""
    from schemas.narrative import NarrativeItem, NarrativeMeta, NarrativeResponse, SourceRef
    from services.pdf_service import generate_pdf
    from datetime import datetime, timezone

    narrative = NarrativeResponse(
        question="Test question for PDF generation?",
        scenario="baseline",
        act1=[NarrativeItem(type="FACT", text="BEV intent is at 38 in 2024.", source="EVForward 2024")],
        act2=[
            NarrativeItem(type="SIGNAL", text="Charging infrastructure is expanding rapidly.", source="Market Events 2024"),
            NarrativeItem(type="INFERENCE", text="Range anxiety will diminish as infrastructure matures."),
        ],
        act3=[NarrativeItem(type="RECOMMENDATION", text="Invest in DC fast charging corridors.", priority=1)],
        sources=[SourceRef(id="ev-2024", title="EVForward 2024", year="2024", category="EVForward Research")],
        confidence=0.85,
        narrative_summary="EV market is at an inflection point.",
        meta=NarrativeMeta(
            request_id="test-123",
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            provider="Test",
            model="test-model",
            latency_ms=500.0,
        ),
    )

    pdf_bytes = generate_pdf(narrative)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes[:4] == b"%PDF"
