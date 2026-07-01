"""
What Next Engine — Streamlit Frontend
======================================
Calls the existing service layer directly — no HTTP, no FastAPI required.

Run:
    streamlit run streamlit_app.py
"""
from __future__ import annotations

import sys
import logging
from pathlib import Path

# ── Ensure project root is importable ────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

# ── Page config (MUST be the very first Streamlit call) ─────────────────────
st.set_page_config(
    page_title="What Next Engine",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "What Next Engine — Escalent EVForward Strategic Intelligence",
    },
)

# ── Logging setup ─────────────────────────────────────────────────────────────
from core.logging_config import setup_logging
setup_logging("INFO")
logger = logging.getLogger(__name__)

# ── Escalent brand CSS ────────────────────────────────────────────────────────
_CSS = """
<style>
/* ── Escalent brand tokens ── */
:root {
    --purple:      #7a00df;
    --purple-dark: #4f0094;
    --purple-mid:  #9b30ff;
    --navy:        #1a3a6b;
    --teal:        #005f73;
    --text:        #3f3f3f;
    --muted:       #666666;
    --bg-alt:      #f5f4fb;
    --white:       #ffffff;
}

/* ── Hide default Streamlit chrome (keep header so Deploy button is visible) ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* ── App background ── */
.stApp { background: #f8f7fc; }

/* ── Hero banner ── */
.nar-hero {
    background: linear-gradient(135deg, var(--purple-dark) 0%, var(--purple) 55%, var(--purple-mid) 100%);
    border-radius: 12px;
    padding: 2rem 2.5rem 1.75rem;
    margin-bottom: 1.5rem;
    color: white;
    position: relative;
    overflow: hidden;
}
.nar-hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.nar-hero-eyebrow {
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.75;
    margin-bottom: 0.4rem;
}
.nar-hero-title {
    font-size: 1.9rem;
    font-weight: 800;
    margin: 0 0 0.5rem;
    line-height: 1.2;
}
.nar-hero-gem { color: #c9a5ff; }
.nar-hero-lead {
    font-size: 0.92rem;
    opacity: 0.88;
    max-width: 600px;
    line-height: 1.6;
    margin-bottom: 1rem;
}
.nar-hero-stats {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
}
.nar-hero-stat { text-align: center; }
.stat-n { display: block; font-size: 1.5rem; font-weight: 800; color: #c9a5ff; }
.stat-l { display: block; font-size: 0.7rem; opacity: 0.75; letter-spacing: 0.05em; }

/* ── Section cards ── */
.nar-card {
    background: white;
    border-radius: 10px;
    border: 1px solid #e8e4f5;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(122,0,223,0.06);
}

/* ── Act banners ── */
.act-banner {
    border-radius: 8px;
    padding: 0.6rem 1.1rem;
    margin: 0.75rem 0 0.5rem;
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    color: white;
}
.act1  { background: linear-gradient(90deg, var(--navy) 0%, #2a5298 100%); }
.act2  { background: linear-gradient(90deg, var(--teal) 0%, #0a8a9f 100%); }
.act3  { background: linear-gradient(90deg, var(--purple-dark) 0%, var(--purple) 100%); }
.act-num   { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
             text-transform: uppercase; opacity: 0.8; }
.act-title { font-size: 1rem; font-weight: 700; }
.act-sub   { font-size: 0.78rem; opacity: 0.75; margin-left: auto; }

/* ── Narrative item cards ── */
.nar-item {
    background: var(--bg-alt);
    border-left: 4px solid var(--purple);
    border-radius: 0 6px 6px 0;
    padding: 0.65rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: var(--text);
    line-height: 1.6;
}
.nar-item.fact  { border-left-color: var(--navy); }
.nar-item.signal   { border-left-color: var(--teal); }
.nar-item.inference{ border-left-color: #e6860a; background: #fffbf3; }
.nar-item.rec   { border-left-color: var(--purple); }
.item-tag {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: white;
    border-radius: 3px;
    padding: 1px 5px;
    margin-right: 6px;
    vertical-align: middle;
}
.tag-fact   { background: var(--navy); }
.tag-signal { background: var(--teal); }
.tag-inference { background: #e6860a; }
.tag-rec    { background: var(--purple); }
.item-source {
    display: block;
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.25rem;
    font-style: italic;
}
.prio-badge {
    float: right;
    font-size: 0.65rem;
    background: var(--purple);
    color: white;
    border-radius: 10px;
    padding: 1px 7px;
    margin-top: 2px;
}

/* ── Source chip ── */
.src-chip {
    display: inline-block;
    background: #ede8fb;
    color: var(--purple-dark);
    border-radius: 20px;
    font-size: 0.72rem;
    padding: 2px 10px;
    margin: 2px 3px;
    font-weight: 500;
}

/* ── Confidence bar ── */
.conf-bar-bg {
    background: #e8e4f5;
    border-radius: 4px;
    height: 8px;
    margin: 0.3rem 0 0.15rem;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--purple), var(--purple-mid));
    transition: width 0.4s ease;
}

/* ── Backtest comparison ── */
.bt-col-header {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.4rem 0.7rem;
    border-radius: 5px 5px 0 0;
    color: white;
    margin-bottom: 0;
}
.bt-predicted { background: var(--navy); }
.bt-actual    { background: var(--teal); }
.bt-item {
    background: #f0f4ff;
    border-radius: 0 0 5px 5px;
    padding: 0.55rem 0.8rem;
    margin-bottom: 0.4rem;
    font-size: 0.88rem;
    color: var(--text);
}
.bt-item.actual-item { background: #eef7f5; }
.bt-item-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--muted);
    letter-spacing: 0.08em;
    display: block;
    margin-bottom: 2px;
}

/* ── Evidence library ── */
.ev-report-card {
    background: white;
    border: 1px solid #e8e4f5;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    transition: box-shadow 0.2s;
}
.ev-report-card:hover { box-shadow: 0 4px 16px rgba(122,0,223,0.12); }
.ev-cat-badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-radius: 3px;
    padding: 1px 6px;
    margin-bottom: 4px;
}
.cat-evforward { background: #ede8fb; color: var(--purple-dark); }
.cat-market    { background: #e0f2f0; color: var(--teal); }
.ev-title { font-size: 0.95rem; font-weight: 700; color: var(--navy); margin: 2px 0; }
.ev-count { font-size: 0.78rem; color: var(--muted); }
.hl-dot {
    font-size: 0.82rem;
    color: var(--text);
    padding: 0.2rem 0;
    border-bottom: 1px solid #f0eefa;
    line-height: 1.5;
}

/* ── Sidebar ── */
.sidebar-brand {
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--purple);
    margin-bottom: 0.15rem;
}
.sidebar-version {
    font-size: 0.7rem;
    color: var(--muted);
    margin-bottom: 1rem;
}
.status-ok   { color: #1a9c5a; font-weight: 700; }
.status-warn { color: #c0750a; font-weight: 700; }
.status-err  { color: #c0180a; font-weight: 700; }

/* ── Summary box ── */
.summary-box {
    background: linear-gradient(135deg, #ede8fb 0%, #f5f4fb 100%);
    border-left: 4px solid var(--purple);
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0 1rem;
    font-size: 0.92rem;
    color: var(--purple-dark);
    font-style: italic;
}

/* ── Generic divider ── */
.nar-divider {
    border: none;
    border-top: 1px solid #e8e4f5;
    margin: 1rem 0;
}

/* ── Quick-start buttons (styled as tags) ── */
div[data-testid="stButton"] > button.qs-btn {
    background: var(--bg-alt);
    border: 1px solid #c9b8f0;
    color: var(--purple-dark);
    border-radius: 20px;
    font-size: 0.78rem;
    padding: 3px 12px;
    margin-right: 4px;
    cursor: pointer;
    transition: background 0.2s;
}
div[data-testid="stButton"] > button.qs-btn:hover {
    background: #ede8fb;
}

/* ── Meta row ── */
.meta-row {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.5rem;
}
.meta-item strong { color: var(--text); }
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Cached service initialisation
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="Warming up ChromaDB…")
def _init_chroma():
    """Initialise ChromaDB collections once per process."""
    from retrieval.chroma_client import get_chroma_collections
    try:
        cols = get_chroma_collections()
        return cols, None
    except Exception as exc:
        logger.warning("ChromaDB init warning: %s", exc)
        return None, str(exc)


@st.cache_data(show_spinner=False)
def _load_evidence_reports():
    """Cache evidence report summaries (no full_content to keep memory lean)."""
    from services.evidence_service import get_evidence_reports
    resp = get_evidence_reports()
    return resp.reports


@st.cache_data(show_spinner=False)
def _get_config():
    from core.config import settings
    from llm.factory import get_provider_display_name
    provider_name, model_name = get_provider_display_name()
    return {
        "provider": provider_name,
        "model": model_name,
        "retrieval_top_k": settings.retrieval_top_k,
        "collections": [
            settings.chroma_evidence_collection,
            settings.chroma_events_collection,
        ],
        "version": settings.app_version,
        "embedding_model": settings.embedding_model,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Session-state defaults
# ═══════════════════════════════════════════════════════════════════════════════

def _init_state():
    defaults = {
        "narrative":       None,
        "backtest":        None,
        "bt_year":         "2024",
        "bt_question":     "What were the key EV market developments and adoption trends?",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ═══════════════════════════════════════════════════════════════════════════════
# Render helpers
# ═══════════════════════════════════════════════════════════════════════════════

_SCENARIOS = {
    "baseline": {
        "label": "Baseline — Current Market Conditions",
        "description": (
            "The EV market continues its current trajectory with existing federal incentives, "
            "moderate infrastructure growth, stable gas prices, and OEM electrification roadmaps on track."
        ),
    },
    "ev_subsidies_rollback": {
        "label": "Federal EV Subsidies Roll Back",
        "description": (
            "Federal EV tax credits are eliminated or significantly reduced. "
            "Consumer price sensitivity rises and OEM EV programmes face revised financial models."
        ),
    },
    "gas_prices_spike": {
        "label": "Gas Prices Spike 20 %",
        "description": (
            "Gasoline prices rise sharply by 20 % or more. "
            "Consumer urgency to switch to lower running-cost vehicles intensifies."
        ),
    },
}

_QUICK_QUESTIONS = [
    ("Adoption barriers",  "What are the primary barriers to mass-market EV adoption and how are they evolving?"),
    ("Intent trends",      "How has BEV purchase intent evolved from 2020 to 2026 and what is driving the shift?"),
    ("Charging gaps",      "What charging infrastructure gaps are most critical to close for mainstream EV adoption?"),
]

_TAG_CSS = {
    "FACT":           ("tag-fact",       "FACT"),
    "SIGNAL":         ("tag-signal",     "SIGNAL"),
    "INFERENCE":      ("tag-inference",  "INFERENCE"),
    "RECOMMENDATION": ("tag-rec",        "REC"),
}

_ITEM_CSS = {
    "FACT":           "fact",
    "SIGNAL":         "signal",
    "INFERENCE":      "inference",
    "RECOMMENDATION": "rec",
}


def _render_item(item) -> str:
    tag_cls, tag_label = _TAG_CSS.get(item.type, ("tag-rec", item.type))
    item_cls = _ITEM_CSS.get(item.type, "rec")
    prio_html = (
        f'<span class="prio-badge">P{item.priority}</span>'
        if item.priority else ""
    )
    src_html = (
        f'<span class="item-source">Source: {item.source}</span>'
        if item.source else ""
    )
    return (
        f'<div class="nar-item {item_cls}">'
        f'{prio_html}'
        f'<span class="item-tag {tag_cls}">{tag_label}</span>'
        f'{item.text}'
        f'{src_html}'
        f'</div>'
    )


def _render_act_banner(num: str, title: str, subtitle: str, cls: str) -> str:
    return (
        f'<div class="act-banner {cls}">'
        f'<span class="act-num">Act {num}</span>'
        f'<span class="act-title">{title}</span>'
        f'<span class="act-sub">{subtitle}</span>'
        f'</div>'
    )


def _render_narrative(narrative):
    """Render the full three-act narrative result."""

    # Narrative summary
    if narrative.narrative_summary:
        st.markdown(
            f'<div class="summary-box">💡 {narrative.narrative_summary}</div>',
            unsafe_allow_html=True,
        )

    # Confidence
    conf = getattr(narrative, "confidence", 0.0)
    conf_pct = int(conf * 100)
    st.markdown(
        f'**Evidence confidence:** {conf_pct}%'
        f'<div class="conf-bar-bg">'
        f'<div class="conf-bar-fill" style="width:{conf_pct}%"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="nar-divider">', unsafe_allow_html=True)

    # ── Act 1 ─────────────────────────────────────────────────────────────────
    st.markdown(
        _render_act_banner("1", "Where They Are", "Grounded Facts", "act1"),
        unsafe_allow_html=True,
    )
    for item in narrative.act1:
        st.markdown(_render_item(item), unsafe_allow_html=True)

    # ── Act 2 ─────────────────────────────────────────────────────────────────
    st.markdown(
        _render_act_banner("2", "Where They Are Heading", "Signals & Inferences", "act2"),
        unsafe_allow_html=True,
    )
    for item in narrative.act2:
        st.markdown(_render_item(item), unsafe_allow_html=True)

    # ── Act 3 ─────────────────────────────────────────────────────────────────
    st.markdown(
        _render_act_banner("3", "Now What", "Strategic Recommendations", "act3"),
        unsafe_allow_html=True,
    )
    sorted_act3 = sorted(narrative.act3, key=lambda x: (x.priority or 99))
    for item in sorted_act3:
        st.markdown(_render_item(item), unsafe_allow_html=True)

    # ── Sources ────────────────────────────────────────────────────────────────
    if narrative.sources:
        st.markdown('<hr class="nar-divider">', unsafe_allow_html=True)
        with st.expander("📎 Evidence Sources", expanded=False):
            chips = "".join(
                f'<span class="src-chip">📄 {s.title} ({s.year})</span>'
                for s in narrative.sources
            )
            st.markdown(chips, unsafe_allow_html=True)

    # ── Meta row ───────────────────────────────────────────────────────────────
    m = narrative.meta
    st.markdown(
        f'<div class="meta-row">'
        f'<span><strong>Provider:</strong> {m.provider}</span>'
        f'<span><strong>Model:</strong> {m.model}</span>'
        f'<span><strong>Latency:</strong> {m.latency_ms:.0f} ms</span>'
        f'<span><strong>ID:</strong> {m.request_id[:8]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_backtest(bt):
    """Render the backtest result."""
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(
            '<div class="bt-col-header bt-predicted">📊 What Was Predicted</div>',
            unsafe_allow_html=True,
        )
        for item in bt.predicted:
            st.markdown(
                f'<div class="bt-item">'
                f'<span class="bt-item-label">{item.label}</span>'
                f'{item.text}'
                f'{"<br><small style=color:#888>Source: " + item.source + "</small>" if item.source else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_r:
        st.markdown(
            '<div class="bt-col-header bt-actual">✅ What Actually Happened</div>',
            unsafe_allow_html=True,
        )
        for item in bt.actual:
            st.markdown(
                f'<div class="bt-item actual-item">'
                f'<span class="bt-item-label">{item.label}</span>'
                f'{item.text}'
                f'{"<br><small style=color:#888>Source: " + item.source + "</small>" if item.source else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )

    if bt.accuracy_note:
        st.info(f"**Accuracy Assessment:** {bt.accuracy_note}")

    m = bt.meta
    st.markdown(
        f'<div class="meta-row">'
        f'<span><strong>Provider:</strong> {m.provider}</span>'
        f'<span><strong>Model:</strong> {m.model}</span>'
        f'<span><strong>Latency:</strong> {m.latency_ms:.0f} ms</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════════════════

def _render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand">◆ What Next Engine</div>'
            '<div class="sidebar-version">Escalent EVForward Intelligence Suite</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        # Coverage stats
        st.markdown("**📊 Coverage**")
        col1, col2 = st.columns(2)
        col1.metric("Report Years", "7")
        col2.metric("Data Range", "2020–26")
        col1.metric("Scenarios", "3")
        col2.metric("Narrative Acts", "3")

        st.divider()

        # System status
        st.markdown("**⚙️ System**")
        cfg = _get_config()
        st.markdown(f"Provider: **{cfg['provider']}**")
        st.markdown(f"Model: `{cfg['model']}`")
        st.markdown(f"Embedding: `{cfg['embedding_model']}`")
        st.markdown(f"Top-K retrieval: **{cfg['retrieval_top_k']}**")
        st.markdown(f"Version: **v{cfg['version']}**")

        st.divider()

        # ChromaDB status
        cols, chroma_err = _init_chroma()
        if cols is not None:
            ev_col, mkt_col = cols
            ev_count = ev_col.count()
            mkt_count = mkt_col.count()
            st.markdown(
                f'<span class="status-ok">● ChromaDB Ready</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"Evidence chunks: {ev_count:,}")
            st.caption(f"Market signal chunks: {mkt_count:,}")
        else:
            st.markdown(
                f'<span class="status-warn">⚠ ChromaDB not ready</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"Run ingestion first: `python run.py --ingest-only`")

        st.divider()
        st.caption("© 2024 Escalent. All rights reserved.")


# ═══════════════════════════════════════════════════════════════════════════════
# Tab: Narrative Generator
# ═══════════════════════════════════════════════════════════════════════════════

def _tab_narrative():
    st.markdown(
        '<div class="nar-card">'
        '<p style="margin:0; font-size:0.9rem; color:#555;">'
        'Enter a strategic question, choose a market scenario, and generate an evidence-grounded '
        'three-act narrative backed by EVForward longitudinal research (2020–2026).'
        '</p></div>',
        unsafe_allow_html=True,
    )

    # ── Input area ────────────────────────────────────────────────────────────
    st.markdown("#### 📝 Strategic Question")

    # Quick-start buttons — write directly to the widget key and rerun so the
    # text area reflects the new value immediately.
    qs_cols = st.columns(len(_QUICK_QUESTIONS) + 1)
    qs_cols[0].markdown("<small style='color:#888'>Quick start:</small>", unsafe_allow_html=True)
    for idx, (qs_label, qs_question) in enumerate(_QUICK_QUESTIONS):
        if qs_cols[idx + 1].button(qs_label, key=f"qs_{idx}", use_container_width=True):
            st.session_state["q_input"] = qs_question
            st.rerun()

    question = st.text_area(
        "Strategic Question",
        height=110,
        max_chars=500,
        placeholder="e.g., How will EV adoption shift given current charging infrastructure investment levels?",
        label_visibility="collapsed",
        key="q_input",
    )
    char_count = len(question)
    st.caption(f"{char_count} / 500 characters {'✓' if char_count >= 10 else '(minimum 10)'}")

    # ── Scenario picker ────────────────────────────────────────────────────────
    st.markdown("#### 🌐 Market Scenario")
    scen_labels = {k: v["label"] for k, v in _SCENARIOS.items()}
    selected_label = st.radio(
        "Scenario",
        options=list(scen_labels.values()),
        key="narrative_scen_radio",
        label_visibility="collapsed",
    )
    selected_scen = next(k for k, v in _SCENARIOS.items() if v["label"] == selected_label)
    st.caption(_SCENARIOS[selected_scen]["description"])

    # ── Generate button ────────────────────────────────────────────────────────
    st.markdown("")
    col_gen, col_clear = st.columns([3, 1])
    generate_clicked = col_gen.button(
        "⚡  Generate Narrative",
        type="primary",
        use_container_width=True,
        disabled=(char_count < 10),
    )
    if col_clear.button("🗑 Clear", use_container_width=True):
        st.session_state["narrative"] = None
        st.session_state["q_input"] = ""
        st.rerun()

    if generate_clicked and char_count >= 10:
        _run_narrative(question, selected_scen)

    # ── Result ─────────────────────────────────────────────────────────────────
    if st.session_state["narrative"] is not None:
        narrative = st.session_state["narrative"]
        st.markdown('<hr class="nar-divider">', unsafe_allow_html=True)
        st.markdown("### 📑 Generated Narrative")
        st.markdown(
            f'**Question:** {narrative.question}  \n'
            f'**Scenario:** {_SCENARIOS.get(narrative.scenario, {}).get("label", narrative.scenario)}'
        )
        _render_narrative(narrative)

        # ── PDF Export ─────────────────────────────────────────────────────────
        st.markdown('<hr class="nar-divider">', unsafe_allow_html=True)
        st.markdown("#### 📥 Export")
        if st.button("Generate PDF Report", use_container_width=False):
            with st.spinner("Building branded PDF…"):
                try:
                    from services.pdf_service import generate_pdf
                    pdf_bytes = generate_pdf(narrative)
                    st.download_button(
                        label="⬇️  Download PDF",
                        data=pdf_bytes,
                        file_name="what_next_engine_report.pdf",
                        mime="application/pdf",
                        use_container_width=False,
                    )
                    st.success("PDF ready — click Download above.")
                except Exception as exc:
                    st.error(f"PDF export failed: {exc}")


def _run_narrative(question: str, scenario: str):
    from schemas.narrative import NarrativeRequest
    from services.narrative_engine import generate_narrative

    request = NarrativeRequest(question=question, scenario=scenario)
    with st.spinner("🔍 Retrieving evidence and generating narrative…"):
        try:
            result = generate_narrative(request)
            st.session_state["narrative"] = result
            st.rerun()
        except RuntimeError as exc:
            st.error(f"**LLM service unavailable:** {exc}")
        except Exception as exc:
            logger.exception("Narrative generation failed")
            st.error(f"**Unexpected error:** {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
# Tab: Backtest Validation
# ═══════════════════════════════════════════════════════════════════════════════

def _tab_backtest():
    st.markdown(
        '<div class="nar-card">'
        '<p style="margin:0; font-size:0.9rem; color:#555;">'
        'Select a year to retrospectively compare what prior data would have predicted '
        'against what actually happened in that year — validating the model\'s foresight.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    _YEARS = ["2021", "2022", "2023", "2024", "2025", "2026"]

    col_year, col_q = st.columns([1, 3])
    with col_year:
        st.markdown("#### 📅 Year")
        year = st.selectbox(
            "Year",
            _YEARS,
            index=_YEARS.index(st.session_state["bt_year"]),
            label_visibility="collapsed",
        )
        st.session_state["bt_year"] = year

    with col_q:
        st.markdown("#### 📝 Analysis Question")
        bt_q = st.text_area(
            "Analysis Question",
            value=st.session_state["bt_question"],
            height=80,
            max_chars=500,
            label_visibility="collapsed",
        )
        st.session_state["bt_question"] = bt_q

    st.markdown("")
    col_run, col_clear = st.columns([3, 1])
    run_clicked = col_run.button(
        f"🔬  Run Backtest for {year}",
        type="primary",
        use_container_width=True,
        disabled=(len(bt_q) < 10),
    )
    if col_clear.button("🗑 Clear", key="bt_clear", use_container_width=True):
        st.session_state["backtest"] = None
        st.rerun()

    if run_clicked and len(bt_q) >= 10:
        _run_backtest(year, bt_q)

    if st.session_state["backtest"] is not None:
        bt = st.session_state["backtest"]
        st.markdown('<hr class="nar-divider">', unsafe_allow_html=True)
        st.markdown(f"### 🔍 Backtest Results — {bt.year}")
        _render_backtest(bt)


def _run_backtest(year: str, question: str):
    from schemas.narrative import BacktestRequest
    from services.validation_service import run_backtest

    request = BacktestRequest(year=year, question=question)
    with st.spinner(f"🔍 Running retrospective analysis for {year}…"):
        try:
            result = run_backtest(request)
            st.session_state["backtest"] = result
            st.rerun()
        except RuntimeError as exc:
            st.error(f"**LLM service unavailable:** {exc}")
        except Exception as exc:
            logger.exception("Backtest failed")
            st.error(f"**Unexpected error:** {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
# (Evidence Library and System Info tabs removed)
# ═══════════════════════════════════════════════════════════════════════════════

def _tab_evidence_REMOVED():
    st.markdown(
        '<div class="nar-card">'
        '<p style="margin:0; font-size:0.9rem; color:#555;">'
        'Browse the full evidence corpus: EVForward longitudinal reports (2020–2026) '
        'and the External Market Event Bank.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Loading evidence library…"):
        try:
            reports = _load_evidence_reports()
        except Exception as exc:
            st.error(f"Could not load evidence reports: {exc}")
            return

    if not reports:
        st.warning("No evidence reports found. Check that `Hackathon Material/` directory exists.")
        return

    # ── Filter bar ─────────────────────────────────────────────────────────────
    col_filter, col_search = st.columns([1, 3])
    with col_filter:
        category_filter = st.selectbox(
            "Category",
            ["All", "EVForward Research", "Market Signals"],
            label_visibility="visible",
        )
    with col_search:
        search_term = st.text_input(
            "Search reports",
            placeholder="Filter by year, title, or keyword…",
            label_visibility="visible",
        )

    # ── Apply filters ──────────────────────────────────────────────────────────
    filtered = reports
    if category_filter != "All":
        filtered = [r for r in filtered if r.category == category_filter]
    if search_term.strip():
        term = search_term.strip().lower()
        filtered = [
            r for r in filtered
            if term in r.title.lower() or term in r.year or term in r.category.lower()
            or any(term in h.lower() for h in r.highlights)
        ]

    st.markdown(f"Showing **{len(filtered)}** of **{len(reports)}** reports")
    st.divider()

    # ── Report cards ───────────────────────────────────────────────────────────
    for report in filtered:
        cat_cls = "cat-evforward" if report.category == "EVForward Research" else "cat-market"
        cat_icon = "📊" if report.category == "EVForward Research" else "📡"

        with st.expander(
            f"{cat_icon} {report.title}  ·  {report.entry_count} entries",
            expanded=False,
        ):
            st.markdown(
                f'<span class="ev-cat-badge {cat_cls}">{report.category}</span>'
                f' <span style="font-size:0.78rem; color:#888">Year: {report.year}'
                f'  |  File: {report.file_name}</span>',
                unsafe_allow_html=True,
            )
            if report.highlights:
                st.markdown("**Key highlights:**")
                for hl in report.highlights:
                    st.markdown(f"- {hl}")
            if report.full_content:
                with st.expander("📄 View full content", expanded=False):
                    st.text_area(
                        "content",
                        value=report.full_content,
                        height=300,
                        disabled=True,
                        label_visibility="collapsed",
                    )


def _tab_system_REMOVED():
    cfg = _get_config()

    st.markdown("### ⚙️ System Configuration")

    col1, col2, col3 = st.columns(3)
    col1.metric("LLM Provider", cfg["provider"])
    col2.metric("Model", cfg["model"])
    col3.metric("App Version", f"v{cfg['version']}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Embedding Model", cfg["embedding_model"])
    col5.metric("Retrieval Top-K", cfg["retrieval_top_k"])
    col6.metric("Python", f"{sys.version_info.major}.{sys.version_info.minor}")

    st.divider()
    st.markdown("### 🗄️ ChromaDB Collections")

    cols, chroma_err = _init_chroma()
    if cols is not None:
        ev_col, mkt_col = cols
        cc1, cc2 = st.columns(2)
        cc1.metric("Evidence Collection", cfg["collections"][0],
                   delta=f"{ev_col.count():,} chunks")
        cc2.metric("Market Events Collection", cfg["collections"][1],
                   delta=f"{mkt_col.count():,} chunks")
        st.success("ChromaDB collections are ready and populated.")
    else:
        st.warning(
            f"ChromaDB collections not ready: `{chroma_err}`\n\n"
            "Run ingestion with:\n```\npython run.py --ingest-only\n```"
        )

    st.divider()
    st.markdown("### 🚀 Ingestion")
    st.info(
        "If this is the first run or you want to re-index the knowledge base, "
        "stop this Streamlit server and run:\n\n"
        "```powershell\n"
        "python run.py --ingest-only\n"
        "```\n"
        "Then restart Streamlit. The ChromaDB data is persistent across restarts."
    )

    st.divider()
    st.markdown("### 📦 Environment")
    st.code(
        f"Python:          {sys.version}\n"
        f"Working dir:     {_ROOT}\n"
        f"ChromaDB dir:    {_ROOT / 'chroma_db'}\n"
        f"Knowledge dir:   {_ROOT / 'knowledge'}\n"
        f"Hackathon data:  {_ROOT / 'Hackathon Material'}",
        language="text",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Main layout
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    _render_sidebar()

    # ── Hero banner ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="nar-hero">'
        '  <div class="nar-hero-eyebrow">Escalent EVForward Intelligence</div>'
        '  <div class="nar-hero-title">'
        '    <span class="nar-hero-gem">◆</span> What Next Engine'
        '  </div>'
        '  <div class="nar-hero-lead">'
        '    Transform EVForward longitudinal research and real-world market signals into '
        '    evidence-grounded, three-act strategic narratives — with full source traceability.'
        '  </div>'
        '  <div class="nar-hero-stats">'
        '    <div class="nar-hero-stat"><span class="stat-n">7</span><span class="stat-l">Report Years</span></div>'
        '    <div class="nar-hero-stat"><span class="stat-n">2020–2026</span><span class="stat-l">EVForward Data</span></div>'
        '    <div class="nar-hero-stat"><span class="stat-n">3</span><span class="stat-l">Scenarios</span></div>'
        '    <div class="nar-hero-stat"><span class="stat-n">3</span><span class="stat-l">Narrative Acts</span></div>'
        '  </div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab_narrative, tab_backtest = st.tabs([
        "⚡ Narrative Generator",
        "🔬 Backtest Validation",
    ])

    with tab_narrative:
        _tab_narrative()

    with tab_backtest:
        _tab_backtest()


if __name__ == "__main__":
    main()
