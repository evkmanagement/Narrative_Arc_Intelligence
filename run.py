"""
Narrative Arc Intelligence Suite — Project Launcher
====================================================

Usage
-----
    python run.py                 Normal startup: ingest (if needed) then serve
    python run.py --ingest        Force re-ingestion then serve
    python run.py --ingest-only   Ingest only, do not start server
    python run.py --server-only   Start server without ingestion
    python run.py --host 0.0.0.0 --port 8080   Custom host/port
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# ── Bootstrap logging early so all stages write to run.log ──────────────────

_ROOT = Path(__file__).resolve().parent

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_ROOT / "run.log", mode="a", encoding="utf-8"),
    ],
    level=logging.INFO,
)
log = logging.getLogger("run")

# ── Ensure project root is importable ────────────────────────────────────────

if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ── Stages ───────────────────────────────────────────────────────────────────

def stage_preflight() -> None:
    log.info("=== STAGE preflight ===")
    log.info("Interpreter : %s", sys.executable)
    major, minor = sys.version_info[:2]
    log.info("Python      : %d.%d", major, minor)
    if (major, minor) < (3, 10):
        log.error("Python 3.10+ is required (found %d.%d). Exiting.", major, minor)
        sys.exit(1)

    env_file = _ROOT / ".env"
    if not env_file.exists():
        example = _ROOT / ".env.example"
        if example.exists():
            env_file.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
            log.warning(".env created from .env.example — add your LLM API key before retrying.")
        else:
            log.warning(".env not found — running with environment variables only.")

    log.info("Preflight OK")


def stage_ingest(force: bool) -> None:
    log.info("=== STAGE ingest  force=%s ===", force)
    try:
        from ingestion.ingestor import run_ingestion
        counts = run_ingestion(force=force)
        log.info(
            "Ingestion complete: %d evidence chunks, %d signal chunks",
            counts["evidence"],
            counts["signals"],
        )
    except Exception:
        log.exception("Ingestion failed")
        sys.exit(1)


def stage_server(host: str, port: int) -> None:
    log.info("=== STAGE server  http://%s:%d ===", host, port)
    try:
        import uvicorn
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info",
        )
    except KeyboardInterrupt:
        log.info("Server stopped by user (KeyboardInterrupt)")
    except Exception:
        log.exception("Server failed to start")
        sys.exit(1)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Narrative Arc Intelligence Suite launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--ingest",       action="store_true", help="Force full re-ingestion")
    parser.add_argument("--ingest-only",  action="store_true", help="Run ingestion only, skip server")
    parser.add_argument("--server-only",  action="store_true", help="Skip ingestion, start server")
    parser.add_argument("--host",         default="0.0.0.0",   help="Server bind host")
    parser.add_argument("--port",         type=int, default=8000, help="Server bind port")
    args = parser.parse_args()

    log.info("=== Narrative Arc Intelligence Suite ===")

    stage_preflight()

    if not args.server_only:
        stage_ingest(force=args.ingest)

    if not args.ingest_only:
        stage_server(host=args.host, port=args.port)

    log.info("=== Run complete ===")


if __name__ == "__main__":
    main()
