"""Branded PDF export using ReportLab."""
from __future__ import annotations

import io
from datetime import datetime, timezone

from core.logging_config import get_logger
from schemas.narrative import NarrativeResponse

logger = get_logger(__name__)

# ── Brand palette (0–1 float RGB) ────────────────────────────────────────────
_PURPLE = "#7a00df"
_PURPLE_DARK = "#4f0094"
_NAVY = "#1a3a6b"
_TEAL = "#005f73"
_TEXT = "#3f3f3f"
_MUTED = "#666666"
_BG_ALT = "#f5f4fb"


def generate_pdf(narrative: NarrativeResponse) -> bytes:
    """Return branded PDF bytes for *narrative*."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            HRFlowable,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:
        raise ImportError("reportlab is required for PDF export: pip install reportlab") from exc

    buf = io.BytesIO()
    page_w, _ = A4
    margin = 18 * mm

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin + 8 * mm, bottomMargin=margin,
    )

    styles = getSampleStyleSheet()

    def _ps(name: str, parent: str = "Normal", **kw) -> ParagraphStyle:
        return ParagraphStyle(name, parent=styles[parent], **kw)

    title_s = _ps("Title", "Heading1", textColor=colors.HexColor(_PURPLE),
                  fontSize=20, spaceAfter=3, fontName="Helvetica-Bold")
    sub_s = _ps("Sub", fontSize=9, textColor=colors.HexColor(_TEXT),
                fontName="Helvetica", spaceAfter=2)
    meta_s = _ps("Meta", fontSize=8, textColor=colors.HexColor(_MUTED),
                 fontName="Helvetica-Oblique")
    tag_s = _ps("Tag", fontSize=9, fontName="Helvetica-Bold",
                textColor=colors.HexColor(_PURPLE))
    body_s = _ps("Body", fontSize=9, leading=14,
                 textColor=colors.HexColor(_TEXT), fontName="Helvetica", spaceAfter=3)
    src_s = _ps("Src", fontSize=8, textColor=colors.HexColor(_MUTED),
                fontName="Helvetica-Oblique", spaceAfter=2)
    act_body_s = _ps("ActBody", fontSize=9, leading=14,
                     textColor=colors.HexColor(_TEXT), fontName="Helvetica",
                     leftIndent=6, spaceAfter=3)

    col_w = page_w - 2 * margin

    def act_banner(num: str, title: str, subtitle: str, bg: str) -> Table:
        white_style = _ps(f"W{num}", fontSize=11, fontName="Helvetica-Bold",
                          textColor=colors.white)
        sub_style = _ps(f"WS{num}", fontSize=8, fontName="Helvetica",
                        textColor=colors.HexColor("#ddddff"))
        t = Table(
            [[Paragraph(f"ACT {num}  {title}", white_style),
              Paragraph(subtitle, sub_style)]],
            colWidths=[col_w * 0.45, col_w * 0.55],
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        return t

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("What Next Engine", title_s))
    story.append(Paragraph("Escalent EVForward Strategic Intelligence Report", sub_s))
    story.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y %H:%M UTC')}  |  "
        f"Provider: {narrative.meta.provider}  |  "
        f"Request: {narrative.meta.request_id[:8]}",
        meta_s,
    ))
    story.append(HRFlowable(width="100%", thickness=2,
                            color=colors.HexColor(_PURPLE), spaceAfter=6))

    # ── Question & Scenario ───────────────────────────────────────────────────
    story.append(Paragraph("<b>Strategic Question</b>", tag_s))
    story.append(Paragraph(narrative.question, body_s))
    story.append(Paragraph(
        f"<b>Scenario:</b> {narrative.scenario.replace('_', ' ').title()}", body_s
    ))
    if narrative.narrative_summary:
        story.append(Paragraph(f"<i>{narrative.narrative_summary}</i>", src_s))
    story.append(Spacer(1, 5 * mm))

    # ── Act 1 ─────────────────────────────────────────────────────────────────
    story.append(act_banner("1", "Where They Are", "Grounded Facts", _NAVY))
    story.append(Spacer(1, 2 * mm))
    for item in narrative.act1:
        story.append(Paragraph(f"<b>[FACT]</b>  {item.text}", act_body_s))
        if item.source:
            story.append(Paragraph(f"Source: {item.source}", src_s))
    story.append(Spacer(1, 4 * mm))

    # ── Act 2 ─────────────────────────────────────────────────────────────────
    story.append(act_banner("2", "Where They Are Heading", "Signals & Inferences", _TEAL))
    story.append(Spacer(1, 2 * mm))
    for item in narrative.act2:
        story.append(Paragraph(f"<b>[{item.type}]</b>  {item.text}", act_body_s))
        if item.source:
            story.append(Paragraph(f"Source: {item.source}", src_s))
    story.append(Spacer(1, 4 * mm))

    # ── Act 3 ─────────────────────────────────────────────────────────────────
    story.append(act_banner("3", "Now What", "Strategic Recommendations", _PURPLE_DARK))
    story.append(Spacer(1, 2 * mm))
    for item in sorted(narrative.act3, key=lambda x: (x.priority or 99)):
        p_label = f"P{item.priority} " if item.priority else ""
        story.append(Paragraph(f"<b>[REC {p_label}]</b>  {item.text}", act_body_s))
    story.append(Spacer(1, 4 * mm))

    # ── Sources ───────────────────────────────────────────────────────────────
    if narrative.sources:
        story.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#cccccc"), spaceAfter=3))
        story.append(Paragraph("<b>Evidence Sources</b>", tag_s))
        for src in narrative.sources:
            story.append(Paragraph(
                f"• {src.title}  ({src.year})  —  {src.category}", src_s
            ))

    doc.build(story)
    logger.info("PDF generated  %.1f KB", len(buf.getvalue()) / 1024)
    return buf.getvalue()
