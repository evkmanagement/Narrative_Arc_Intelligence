# Narrative Arc Intelligence Suite

Escalent-branded, AI-enabled strategic intelligence application that converts EVForward
research evidence and external market signals into a structured three-act narrative.

## Quick Start

### 1. Set up Python 3.11 virtual environment

```powershell
python -m venv .venv311
.venv311\Scripts\activate
pip install -r requirements.txt
```

> **Note:** `sentence-transformers` downloads the `all-MiniLM-L6-v2` embedding model
> (~90 MB) on first run. An internet connection is required for the first launch.

### 2. Configure environment variables

```powershell
copy .env.example .env
# Edit .env and add your LLM API key
```

Set `LLM_PROVIDER` to one of: `openai`, `azure_openai`, `claude`, `gemini`
and fill in the corresponding API key/endpoint.

### 3. Ingest the knowledge base (first run only)

```powershell
.venv311\Scripts\python.exe run.py --ingest-only
```

This parses all Hackathon Material files and populates ChromaDB. Only required once;
data persists across restarts.

### 4a. Run the Streamlit web app (recommended — shareable)

```powershell
.venv311\Scripts\streamlit.exe run streamlit_app.py
```

Opens automatically at **http://localhost:8501**.  
Share with teammates by exposing the port or deploying to **Streamlit Community Cloud**.

### 4b. Run the original FastAPI server (API + vanilla-JS frontend)

```powershell
# Full startup (ingest + server)
.venv311\Scripts\python.exe run.py

# Start server only (skip ingestion)
.venv311\Scripts\python.exe run.py --server-only
```

Open **http://localhost:8000** in your browser.  
API documentation is available at **http://localhost:8000/api/docs**.

---

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub (add your secrets to `.streamlit/secrets.toml` or via the Cloud dashboard).
2. Point the app to `streamlit_app.py`.
3. Set environment variables (`LLM_PROVIDER`, API keys) in the Streamlit Cloud **Secrets** panel.

---

## Running Tests

```powershell
.venv311\Scripts\python.exe -m pytest -q
```

Expected: all tests pass. Tests mock LLM calls — no API key required for testing.

---

## Project Structure

```
Narrative Arc_v1.1/
├── api/                    FastAPI application & routers
│   ├── main.py             App factory, lifespan, static file mounting
│   └── routers/            health, config, scenarios, analyze, backtest, evidence, export
├── core/                   Configuration & logging
│   ├── config.py           Settings (pydantic-settings) + derived paths
│   └── logging_config.py   Console + run.log handler setup
├── schemas/                Pydantic request/response models
├── llm/                    LLM provider abstraction
│   ├── base.py             Abstract base + JSON repair
│   ├── factory.py          Provider selection with fallback
│   └── *_provider.py       OpenAI, Azure OpenAI, Claude, Gemini
├── ingestion/
│   └── ingestor.py         Parse Hackathon Material → ChromaDB + knowledge files
├── retrieval/
│   ├── chroma_client.py    Singleton ChromaDB client + embedding function
│   └── retriever.py        Semantic search helpers
├── services/
│   ├── narrative_engine.py Three-act narrative generation (RAG + LLM)
│   ├── validation_service.py Backtest / retrospective analysis
│   ├── evidence_service.py  Report summary aggregation
│   └── pdf_service.py       Branded PDF export via ReportLab
├── frontend/
│   ├── index.html          Single-page application
│   ├── css/styles.css      Escalent design system tokens + full component styles
│   └── js/app.js           Vanilla JS ES6+ SPA logic
├── tests/                  pytest suite (LLM fully mocked)
├── Hackathon Material/     Source corpus (EVForward + Market Event Bank)
├── knowledge/              Generated: evidence_bank.txt, market_events.txt
├── chroma_db/              Generated: ChromaDB persistence
├── run.log                 Generated: stage-based runtime log
├── run.py                  Launcher: preflight → ingest → server
├── requirements.txt
└── .env.example
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET  | `/api/v1/health`           | Health check |
| GET  | `/api/v1/config`           | Runtime configuration |
| GET  | `/api/v1/scenarios`        | Available scenarios |
| POST | `/api/v1/analyze`          | Generate three-act narrative |
| POST | `/api/v1/backtest`         | Retrospective validation |
| GET  | `/api/v1/evidence/reports` | Evidence report summaries |
| POST | `/api/export/pdf`          | Export narrative as branded PDF |

All endpoints are also accessible without the `/v1` prefix.

---

## Scenarios

| ID | Label |
|----|-------|
| `baseline` | Baseline — Current Market Conditions |
| `ev_subsidies_rollback` | Federal EV Subsidies Roll Back |
| `gas_prices_spike` | Gas Prices Spike 20 % |

---

## LLM Providers

Set `LLM_PROVIDER` in `.env` to select the active provider.
The application automatically falls back to alternate providers if the primary is unavailable.

| Provider | Env Var |
|----------|---------|
| OpenAI | `OPENAI_API_KEY` |
| Azure OpenAI | `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` |
| Anthropic Claude | `ANTHROPIC_API_KEY` |
| Google Gemini | `GOOGLE_API_KEY` |

---

## Troubleshooting

**ChromaDB / embedding model issues:**
The embedding model is downloaded from HuggingFace on first run. If you're behind a proxy,
set `HF_DATASETS_OFFLINE=1` and manually download `all-MiniLM-L6-v2`.

**LLM provider unavailable:**
Check `.env` for correct keys. The app falls back to alternates if available.

**Tests fail with import errors:**
Ensure you activated the virtual environment before running pytest.

**Ingestion finds no files:**
Verify `Hackathon Material/` exists at the project root with the correct subdirectory names.
