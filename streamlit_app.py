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

# ── Design system CSS ───────────────────────────────────────────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Design tokens ── */
:root {
    --brand:        #6200ea;
    --brand-dark:   #3700b3;
    --brand-light:  #bb86fc;
    --navy:         #1a237e;
    --teal:         #004d40;
    --amber:        #e65100;
    --surface:      #ffffff;
    --surface-2:    #f8f9fa;
    --border:       #e0e0e0;
    --text-1:       #1a1a2e;
    --text-2:       #5f6368;
    --text-3:       #9e9e9e;
    --shadow-sm:    0 1px 3px rgba(0,0,0,0.08),0 1px 2px rgba(0,0,0,0.05);
    --shadow-md:    0 4px 12px rgba(0,0,0,0.08),0 2px 4px rgba(0,0,0,0.05);
    --shadow-lg:    0 10px 24px rgba(0,0,0,0.09),0 4px 8px rgba(0,0,0,0.05);
    --r-sm: 6px; --r-md: 10px; --r-lg: 14px;
}

/* ── Base ── */
html,body,[class*="css"],.stApp {
    font-family: 'Inter',-apple-system,BlinkMacSystemFont,sans-serif !important;
}
#MainMenu{visibility:hidden;}footer{visibility:hidden;}
.stApp { background:#f0f2f6; }
.main .block-container { padding:1rem 2rem 3rem; max-width:1440px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#12113a 0%,#1a1a2e 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label { color:#d0d0e8 !important; }
[data-testid="stSidebar"] [data-testid="stMetricValue"] { color:#bb86fc !important; font-weight:700 !important; }
[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color:rgba(255,255,255,0.45) !important; font-size:0.68rem !important; }
[data-testid="stSidebar"] [data-testid="metric-container"] {
    background:rgba(255,255,255,0.05) !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    border-radius:var(--r-sm) !important;
}
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,0.08) !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background:white;
    border-radius:var(--r-md);
    padding:4px;
    gap:4px;
    border:1px solid var(--border);
    box-shadow:var(--shadow-sm);
    margin-bottom:1.25rem;
}
[data-testid="stTabs"] button[role="tab"] {
    border-radius:var(--r-sm) !important;
    font-weight:500 !important;
    font-size:0.85rem !important;
    color:var(--text-2) !important;
    padding:0.45rem 1.2rem !important;
    transition:all 0.2s !important;
    border:none !important;
    letter-spacing:0.01em !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background:var(--brand) !important;
    color:white !important;
    box-shadow:0 2px 8px rgba(98,0,234,0.35) !important;
}

/* ── Primary button ── */
[data-testid="stButton"] > button[kind="primary"] {
    background:linear-gradient(135deg,var(--brand) 0%,var(--brand-dark) 100%) !important;
    border:none !important;
    border-radius:var(--r-sm) !important;
    font-weight:600 !important;
    letter-spacing:0.02em !important;
    box-shadow:0 2px 10px rgba(98,0,234,0.3) !important;
    transition:all 0.2s !important;
    font-family:'Inter',sans-serif !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow:0 4px 18px rgba(98,0,234,0.45) !important;
    transform:translateY(-1px) !important;
}
[data-testid="stButton"] > button[kind="secondary"] {
    border:1.5px solid var(--border) !important;
    color:var(--text-2) !important;
    border-radius:var(--r-sm) !important;
    font-weight:500 !important;
    background:white !important;
    font-family:'Inter',sans-serif !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color:#9c6fe0 !important;
    color:var(--brand) !important;
}

/* ── Inputs ── */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    border:1.5px solid var(--border) !important;
    border-radius:var(--r-sm) !important;
    font-family:'Inter',sans-serif !important;
    font-size:0.9rem !important;
    color:var(--text-1) !important;
    background:white !important;
    transition:border-color 0.2s,box-shadow 0.2s !important;
    box-shadow:var(--shadow-sm) !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color:var(--brand) !important;
    box-shadow:0 0 0 3px rgba(98,0,234,0.12) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"]>div>div {
    border:1.5px solid var(--border) !important;
    border-radius:var(--r-sm) !important;
    background:white !important;
    box-shadow:var(--shadow-sm) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border:1px solid var(--border) !important;
    border-radius:var(--r-md) !important;
    background:white !important;
    box-shadow:var(--shadow-sm) !important;
}
[data-testid="stExpander"] summary {
    font-weight:600 !important;
    font-size:0.85rem !important;
    color:var(--text-1) !important;
}

/* ── Radio ── */
[data-testid="stRadio"]>label { display:none !important; }
[data-testid="stRadio"]>div { gap:0.4rem !important; }
[data-testid="stRadio"]>div>label {
    background:white !important;
    border:1.5px solid var(--border) !important;
    border-radius:var(--r-sm) !important;
    padding:0.55rem 1rem !important;
    cursor:pointer !important;
    transition:all 0.18s !important;
    font-size:0.83rem !important;
    font-weight:500 !important;
    color:var(--text-2) !important;
    box-shadow:var(--shadow-sm) !important;
}
[data-testid="stRadio"]>div>label:hover {
    border-color:#9c6fe0 !important;
    color:var(--brand) !important;
}
[data-testid="stRadio"]>div>label:has(input:checked) {
    border-color:var(--brand) !important;
    background:#f3e5ff !important;
    color:var(--brand-dark) !important;
    font-weight:600 !important;
}

/* ═══ CUSTOM COMPONENTS ═══ */

/* Topbar */
.wne-topbar {
    background:linear-gradient(135deg,#12113a 0%,#1a1a2e 55%,#0f3460 100%);
    border-radius:var(--r-lg);
    padding:1.15rem 2rem;
    margin-bottom:1.1rem;
    display:flex;
    align-items:center;
    justify-content:space-between;
    box-shadow:var(--shadow-lg);
    position:relative;
    overflow:hidden;
}
.wne-topbar::after {
    content:"";
    position:absolute;
    right:-30px; top:-30px;
    width:160px; height:160px;
    background:radial-gradient(circle,rgba(98,0,234,0.3) 0%,transparent 70%);
    border-radius:50%;
    pointer-events:none;
}
.wne-logo { display:flex; align-items:center; gap:0.7rem; }
.wne-gem  { font-size:1.6rem; color:#bb86fc; line-height:1; }
.wne-app-name  { font-size:1.25rem; font-weight:800; color:white; letter-spacing:-0.02em; }
.wne-app-tag   { font-size:0.62rem; color:rgba(255,255,255,0.45); letter-spacing:0.13em; text-transform:uppercase; margin-top:1px; }
.wne-kpis {
    display:flex;
    align-items:center;
    gap:0;
}
.wne-kpi {
    text-align:center;
    padding:0 1.2rem;
    border-left:1px solid rgba(255,255,255,0.1);
}
.wne-kpi-v { font-size:1.15rem; font-weight:800; color:#bb86fc; display:block; line-height:1.1; }
.wne-kpi-l { font-size:0.6rem; color:rgba(255,255,255,0.45); text-transform:uppercase; letter-spacing:0.1em; }

/* Sidebar brand */
.sb-brand { display:flex; align-items:center; gap:0.55rem; margin-bottom:2px; }
.sb-gem   { font-size:1.1rem; color:#bb86fc; }
.sb-name  { font-size:0.92rem; font-weight:800; color:white; letter-spacing:-0.01em; }
.sb-tag   { font-size:0.6rem; color:rgba(255,255,255,0.35); letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.65rem; }
.sb-section { font-size:0.58rem; font-weight:700; letter-spacing:0.18em; text-transform:uppercase;
              color:rgba(255,255,255,0.28); margin:0.8rem 0 0.35rem; }
.sb-row { display:flex; justify-content:space-between; align-items:center;
          padding:0.28rem 0; border-bottom:1px solid rgba(255,255,255,0.05);
          font-size:0.74rem; }
.sb-row:last-child { border-bottom:none; }
.sb-k { color:rgba(255,255,255,0.4); }
.sb-v { color:rgba(255,255,255,0.82); font-weight:500; font-size:0.71rem; text-align:right; max-width:60%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.sb-ok   { color:#69f0ae; font-weight:600; font-size:0.78rem; }
.sb-warn { color:#ffd740; font-weight:600; font-size:0.78rem; }

/* Form card */
.wne-card {
    background:white;
    border-radius:var(--r-lg);
    border:1px solid var(--border);
    padding:1.4rem 1.6rem;
    margin-bottom:1.1rem;
    box-shadow:var(--shadow-md);
}
.wne-field-label {
    font-size:0.65rem;
    font-weight:700;
    letter-spacing:0.13em;
    text-transform:uppercase;
    color:var(--brand);
    margin-bottom:0.4rem;
    display:block;
}
.wne-divider { border:none; border-top:1px solid #f0f0f0; margin:1.1rem 0; }
.wne-char-ct { font-size:0.7rem; color:var(--text-3); text-align:right; margin-top:-0.3rem; margin-bottom:0.4rem; }

/* Quick-start pills (qs) */
.wne-qs-wrap { display:flex; align-items:center; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.55rem; }
.wne-qs-lbl  { font-size:0.68rem; color:var(--text-3); font-weight:500; flex-shrink:0; }

/* Summary */
.wne-summary {
    background:linear-gradient(135deg,#f3e5ff 0%,#ede7f6 100%);
    border-left:4px solid var(--brand);
    border-radius:0 var(--r-md) var(--r-md) 0;
    padding:0.85rem 1.1rem;
    margin-bottom:1rem;
    font-size:0.9rem;
    color:#3700b3;
    font-style:italic;
    font-weight:500;
    line-height:1.65;
    box-shadow:var(--shadow-sm);
}

/* Confidence row */
.wne-conf {
    display:flex;
    align-items:center;
    gap:0.7rem;
    background:white;
    border:1px solid var(--border);
    border-radius:var(--r-sm);
    padding:0.55rem 0.9rem;
    margin-bottom:1rem;
    box-shadow:var(--shadow-sm);
}
.wne-conf-lbl   { font-size:0.72rem; font-weight:600; color:var(--text-2); white-space:nowrap; }
.wne-conf-track { flex:1; background:#ede7f6; border-radius:10px; height:6px; overflow:hidden; }
.wne-conf-fill  { height:100%; border-radius:10px; background:linear-gradient(90deg,var(--brand),var(--brand-light)); }
.wne-conf-pct   { font-size:0.78rem; font-weight:700; color:var(--brand); min-width:34px; text-align:right; }

/* Act column card */
.wne-act {
    background:white;
    border:1px solid var(--border);
    border-radius:var(--r-lg);
    overflow:hidden;
    box-shadow:var(--shadow-md);
    height:100%;
}
.wne-act-hd { padding:0.8rem 1rem; color:white; }
.hd1 { background:linear-gradient(135deg,#1a237e 0%,#283593 100%); }
.hd2 { background:linear-gradient(135deg,#004d40 0%,#00695c 100%); }
.hd3 { background:linear-gradient(135deg,#4a148c 0%,#6a1b9a 100%); }
.wne-act-eye   { font-size:0.58rem; font-weight:700; letter-spacing:0.2em; text-transform:uppercase; opacity:0.65; }
.wne-act-title { font-size:0.92rem; font-weight:700; line-height:1.2; }
.wne-act-sub   { font-size:0.68rem; opacity:0.7; margin-top:1px; }
.wne-act-body  { padding:0.8rem 0.85rem; }

/* Narrative items */
.wne-item {
    border:1px solid #efefef;
    border-left:3px solid #ccc;
    border-radius:var(--r-sm);
    padding:0.55rem 0.7rem;
    margin-bottom:0.45rem;
    font-size:0.81rem;
    color:var(--text-1);
    line-height:1.55;
    background:#fafafa;
    transition:box-shadow 0.15s;
}
.wne-item:hover { box-shadow:var(--shadow-sm); }
.wne-item.fact  { border-left-color:#1a237e; background:#f8f9ff; border-color:#e8eaf6; }
.wne-item.sig   { border-left-color:#004d40; background:#f8fffd; border-color:#e0f2f1; }
.wne-item.inf   { border-left-color:#e65100; background:#fffbf5; border-color:#ffe0cc; }
.wne-item.rec   { border-left-color:#4a148c; background:#fdf8ff; border-color:#e8d5f7; }
.wne-tag {
    display:inline-block;
    font-size:0.58rem; font-weight:700;
    letter-spacing:0.1em; text-transform:uppercase;
    color:white; border-radius:3px;
    padding:1px 5px; margin-right:5px; vertical-align:middle;
}
.t-fact { background:#1a237e; }
.t-sig  { background:#004d40; }
.t-inf  { background:#e65100; }
.t-rec  { background:#4a148c; }
.wne-prio {
    float:right; font-size:0.6rem; font-weight:700;
    background:#4a148c; color:white;
    border-radius:10px; padding:1px 6px;
}
.wne-src {
    display:block; font-size:0.69rem;
    color:var(--text-3); margin-top:0.2rem; font-style:italic;
}

/* Source chips */
.wne-chip {
    display:inline-block;
    background:#ede7f6; color:#4a148c;
    border:1px solid #d1c4e9;
    border-radius:20px; font-size:0.69rem;
    padding:2px 9px; margin:2px 3px; font-weight:500;
}

/* Meta strip */
.wne-meta {
    display:flex; gap:0;
    background:#f8f9fa;
    border:1px solid var(--border);
    border-radius:var(--r-sm);
    overflow:hidden; margin-top:0.85rem;
}
.wne-meta-cell {
    flex:1; padding:0.4rem 0.75rem;
    border-right:1px solid var(--border);
    font-size:0.7rem; color:var(--text-3);
}
.wne-meta-cell:last-child { border-right:none; }
.wne-meta-cell strong { color:var(--text-2); display:block; font-size:0.64rem; margin-bottom:1px; }

/* Backtest panels */
.wne-bt {
    background:white;
    border:1px solid var(--border);
    border-radius:var(--r-lg);
    overflow:hidden;
    box-shadow:var(--shadow-md);
    height:100%;
}
.wne-bt-hd {
    padding:0.7rem 1rem;
    color:white; font-size:0.78rem;
    font-weight:700; letter-spacing:0.06em;
    text-transform:uppercase;
}
.wne-bt-hd-p { background:linear-gradient(135deg,#1a237e,#283593); }
.wne-bt-hd-a { background:linear-gradient(135deg,#004d40,#00695c); }
.wne-bt-body { padding:0.7rem; }
.wne-bt-item {
    background:#f8f9ff;
    border:1px solid #e8eaf6;
    border-radius:var(--r-sm);
    padding:0.55rem 0.7rem;
    margin-bottom:0.4rem;
    font-size:0.81rem;
    color:var(--text-1);
    line-height:1.5;
}
.wne-bt-item.actual { background:#f8fffd; border-color:#e0f2f1; }
.wne-bt-item-lbl {
    font-size:0.6rem; font-weight:700;
    text-transform:uppercase; color:var(--text-3);
    letter-spacing:0.08em; display:block; margin-bottom:3px;
}
.wne-accuracy {
    background:linear-gradient(135deg,#fff8e1,#fff3e0);
    border:1px solid #ffe082;
    border-left:4px solid #f9a825;
    border-radius:0 var(--r-sm) var(--r-sm) 0;
    padding:0.7rem 1rem;
    margin-top:0.75rem;
    font-size:0.83rem;
    color:#5d4037;
    line-height:1.6;
}
.wne-results-q {
    font-size:0.83rem; color:var(--text-2); margin-bottom:3px;
    display:flex; align-items:center; gap:0.4rem;
}
.wne-results-scen {
    display:inline-block;
    background:#ede7f6; color:#4a148c;
    border-radius:20px; font-size:0.68rem; font-weight:600;
    padding:2px 9px; margin-left:4px;
}
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


_ITEM_MAP = {
    "FACT":           ("t-fact", "FACT",   "fact"),
    "SIGNAL":         ("t-sig",  "SIGNAL", "sig"),
    "INFERENCE":      ("t-inf",  "INFER",  "inf"),
    "RECOMMENDATION": ("t-rec",  "REC",    "rec"),
}


def _render_item(item) -> str:
    tag_cls, tag_label, item_cls = _ITEM_MAP.get(item.type, ("t-rec", item.type, "rec"))
    prio = f'<span class="wne-prio">P{item.priority}</span>' if item.priority else ""
    src  = f'<span class="wne-src">📎 {item.source}</span>' if item.source else ""
    return (
        f'<div class="wne-item {item_cls}">'
        f'{prio}<span class="wne-tag {tag_cls}">{tag_label}</span>'
        f'{item.text}{src}</div>'
    )


def _render_narrative(narrative):
    """Render the full three-act narrative result."""

    # Summary callout
    if narrative.narrative_summary:
        st.markdown(
            f'<div class="wne-summary">💡 {narrative.narrative_summary}</div>',
            unsafe_allow_html=True,
        )

    # Confidence bar
    conf     = getattr(narrative, "confidence", 0.0)
    conf_pct = int(conf * 100)
    st.markdown(
        f'<div class="wne-conf">'
        f'<span class="wne-conf-lbl">Evidence Confidence</span>'
        f'<div class="wne-conf-track"><div class="wne-conf-fill" style="width:{conf_pct}%"></div></div>'
        f'<span class="wne-conf-pct">{conf_pct}%</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Three acts — equal columns
    col1, col2, col3 = st.columns(3, gap="small")

    _ACTS = [
        (col1, "1", "Where They Are",       "Grounded Facts",            "hd1", narrative.act1),
        (col2, "2", "Where They Are Heading","Signals & Inferences",      "hd2", narrative.act2),
        (col3, "3", "Now What",              "Strategic Recommendations", "hd3",
         sorted(narrative.act3, key=lambda x: (x.priority or 99))),
    ]
    for col, num, title, sub, hd_cls, items in _ACTS:
        with col:
            st.markdown(
                f'<div class="wne-act">'
                f'<div class="wne-act-hd {hd_cls}">'
                f'<span class="wne-act-eye">Act {num}</span>'
                f'<div class="wne-act-title">{title}</div>'
                f'<div class="wne-act-sub">{sub}</div>'
                f'</div>'
                f'<div class="wne-act-body">'
                + "".join(_render_item(i) for i in items)
                + "</div></div>",
                unsafe_allow_html=True,
            )

    # Sources
    if narrative.sources:
        st.markdown("")
        with st.expander(f"📎 Evidence Sources ({len(narrative.sources)})", expanded=False):
            chips = "".join(
                f'<span class="wne-chip">{s.title} &middot; {s.year}</span>'
                for s in narrative.sources
            )
            st.markdown(chips, unsafe_allow_html=True)

    # Meta strip
    m = narrative.meta
    st.markdown(
        f'<div class="wne-meta">'
        f'<div class="wne-meta-cell"><strong>Provider</strong>{m.provider}</div>'
        f'<div class="wne-meta-cell"><strong>Model</strong>{m.model}</div>'
        f'<div class="wne-meta-cell"><strong>Latency</strong>{m.latency_ms:.0f} ms</div>'
        f'<div class="wne-meta-cell"><strong>Request ID</strong>{m.request_id[:8]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_backtest(bt):
    """Render the backtest result."""
    col_l, col_r = st.columns(2, gap="medium")

    def _bt_items(items, css_extra=""):
        return "".join(
            f'<div class="wne-bt-item {css_extra}">'
            f'<span class="wne-bt-item-lbl">{i.label}</span>'
            f'{i.text}'
            + (f'<span class="wne-src">📎 {i.source}</span>' if i.source else "")
            + "</div>"
            for i in items
        )

    with col_l:
        st.markdown(
            f'<div class="wne-bt">'
            f'<div class="wne-bt-hd wne-bt-hd-p">📊 What Was Predicted</div>'
            f'<div class="wne-bt-body">{_bt_items(bt.predicted)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_r:
        st.markdown(
            f'<div class="wne-bt">'
            f'<div class="wne-bt-hd wne-bt-hd-a">✅ What Actually Happened</div>'
            f'<div class="wne-bt-body">{_bt_items(bt.actual, "actual")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if bt.accuracy_note:
        st.markdown(
            f'<div class="wne-accuracy">📊 <strong>Accuracy Assessment</strong><br>{bt.accuracy_note}</div>',
            unsafe_allow_html=True,
        )

    m = bt.meta
    st.markdown(
        f'<div class="wne-meta">'
        f'<div class="wne-meta-cell"><strong>Provider</strong>{m.provider}</div>'
        f'<div class="wne-meta-cell"><strong>Model</strong>{m.model}</div>'
        f'<div class="wne-meta-cell"><strong>Latency</strong>{m.latency_ms:.0f} ms</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════════════════

def _render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown(
            '<div class="sb-brand"><span class="sb-gem">◆</span>'
            '<span class="sb-name">What Next Engine</span></div>'
            '<div class="sb-tag">Escalent EVForward Intelligence</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        # Coverage KPIs
        st.markdown('<div class="sb-section">Coverage</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Report Years", "7")
        c2.metric("Data Range", "2020–26")
        c1.metric("Scenarios", "3")
        c2.metric("Acts", "3")

        st.divider()

        # System config
        st.markdown('<div class="sb-section">Configuration</div>', unsafe_allow_html=True)
        cfg = _get_config()
        rows = [
            ("Provider",   cfg["provider"]),
            ("Model",      cfg["model"]),
            ("Embedding",  cfg["embedding_model"]),
            ("Top-K",      str(cfg["retrieval_top_k"])),
            ("Version",    f"v{cfg['version']}"),
        ]
        html = "".join(
            f'<div class="sb-row"><span class="sb-k">{k}</span>'
            f'<span class="sb-v" title="{v}">{v}</span></div>'
            for k, v in rows
        )
        st.markdown(html, unsafe_allow_html=True)

        st.divider()

        # Knowledge base status
        st.markdown('<div class="sb-section">Knowledge Base</div>', unsafe_allow_html=True)
        cols, chroma_err = _init_chroma()
        if cols is not None:
            ev_col, mkt_col = cols
            ev_n, mkt_n = ev_col.count(), mkt_col.count()
            st.markdown('<span class="sb-ok">●  Connected</span>', unsafe_allow_html=True)
            kb_rows = [
                ("Evidence chunks",  f"{ev_n:,}"),
                ("Signal chunks",    f"{mkt_n:,}"),
            ]
            kb_html = "".join(
                f'<div class="sb-row"><span class="sb-k">{k}</span><span class="sb-v">{v}</span></div>'
                for k, v in kb_rows
            )
            st.markdown(kb_html, unsafe_allow_html=True)
        else:
            st.markdown('<span class="sb-warn">⚠  Not ready</span>', unsafe_allow_html=True)
            st.caption("Run: `python run.py --ingest-only`")

        st.divider()
        st.caption("© 2025 Escalent. All rights reserved.")


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
    from services.narrative_engine import OutOfScopeError, generate_narrative

    request = NarrativeRequest(question=question, scenario=scenario)
    with st.spinner("🔍 Retrieving evidence and generating narrative…"):
        try:
            result = generate_narrative(request)
            st.session_state["narrative"] = result
            st.rerun()
        except OutOfScopeError as exc:
            st.warning(
                f"⚠️ **Question outside EVForward scope**\n\n"
                f"{exc.reason}\n\n"
                "This tool is grounded exclusively in Escalent EVForward longitudinal research "
                "(2020–2026) and covers electric vehicles, EV adoption, charging infrastructure, "
                "automotive electrification, and related topics. "
                "Please rephrase your question within that domain."
            )
        except RuntimeError as exc:
            st.error(f"**LLM service unavailable:** {exc}")
        except Exception as exc:
            logger.exception("Narrative generation failed")
            st.error(f"**Unexpected error:** {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
# Tab: Backtest Validation
# ═══════════════════════════════════════════════════════════════════════════════

def _tab_backtest():
    _YEARS = ["2021", "2022", "2023", "2024", "2025", "2026"]

    with st.container():
        st.markdown('<div class="wne-card">', unsafe_allow_html=True)

        col_year, col_q = st.columns([1, 3], gap="medium")
        with col_year:
            st.markdown('<span class="wne-field-label">Analysis Year</span>', unsafe_allow_html=True)
            year = st.selectbox(
                "Year",
                _YEARS,
                index=_YEARS.index(st.session_state["bt_year"]),
                label_visibility="collapsed",
            )
            st.session_state["bt_year"] = year
            st.caption("Retrospective window: prior years vs selected year")

        with col_q:
            st.markdown('<span class="wne-field-label">Research Question</span>', unsafe_allow_html=True)
            bt_q = st.text_area(
                "Analysis Question",
                value=st.session_state["bt_question"],
                height=90,
                max_chars=500,
                label_visibility="collapsed",
            )
            st.session_state["bt_question"] = bt_q

        st.markdown('<hr class="wne-divider">', unsafe_allow_html=True)

        col_run, col_clear, col_spacer = st.columns([3, 1, 2])
        run_clicked = col_run.button(
            f"🔬  Run Backtest — {year}",
            type="primary",
            use_container_width=True,
            disabled=(len(bt_q) < 10),
        )
        if col_clear.button("↺  Clear", key="bt_clear", use_container_width=True):
            st.session_state["backtest"] = None
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    if run_clicked and len(bt_q) >= 10:
        _run_backtest(year, bt_q)

    if st.session_state["backtest"] is not None:
        bt = st.session_state["backtest"]
        st.divider()
        st.markdown(
            f'<div class="wne-results-q">🔍'
            f' Retrospective analysis for <strong>{bt.year}</strong>'
            f' &mdash; <em style="font-size:0.8rem">{bt.question[:90]}&hellip;</em>'
            f'</div>',
            unsafe_allow_html=True,
        )
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

    # ── Topbar ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="wne-topbar">'
        '  <div class="wne-logo">'
        '    <span class="wne-gem">◆</span>'
        '    <div><div class="wne-app-name">What Next Engine</div>'
        '    <div class="wne-app-tag">Escalent EVForward Strategic Intelligence</div></div>'
        '  </div>'
        '  <div class="wne-kpis">'
        '    <div class="wne-kpi"><span class="wne-kpi-v">7</span><span class="wne-kpi-l">Report Years</span></div>'
        '    <div class="wne-kpi"><span class="wne-kpi-v">2020–2026</span><span class="wne-kpi-l">EVForward Data</span></div>'
        '    <div class="wne-kpi"><span class="wne-kpi-v">3</span><span class="wne-kpi-l">Scenarios</span></div>'
        '    <div class="wne-kpi"><span class="wne-kpi-v">3</span><span class="wne-kpi-l">Narrative Acts</span></div>'
        '  </div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab_narrative, tab_backtest = st.tabs([
        "⚡  Narrative Generator",
        "🔬  Backtest Validation",
    ])

    with tab_narrative:
        _tab_narrative()

    with tab_backtest:
        _tab_backtest()


if __name__ == "__main__":
    main()
