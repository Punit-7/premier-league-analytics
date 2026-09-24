"""Append one JSON line per pipeline stage to logs/runs.jsonl.

Why JSONL and not straight into DuckDB: ingest runs before the database
exists, and a logger that depends on the thing it is logging about cannot
record the failure to build it. load.py reads this file into a
pipeline_run table at the end, so the history ends up queryable anyway.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from src.logging_setup import LOG_DIR, RUN_ID

RUNS = LOG_DIR / "runs.jsonl"

def record(stage: str, status: str, duration_s: float, rows: int | None=None, message: str = "") -> None:
    
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "run_id": RUN_ID,
        "stage": stage,
        "status": status,
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duration_s": round(duration_s, 2),
        "rows": rows,
        "message": message[:500],
    }
    
    with open(RUNS, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
        
        
def read_all() -> list[dict]:
    if not RUNS.exists():
        return []
    return [json.loads(line) for line in RUNS.read_text(encoding="utf-8").splitlines() if line.strip()]


