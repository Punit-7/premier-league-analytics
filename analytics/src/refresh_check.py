"""Event detection: has a new gameweek finished since the last refresh?

The workflow runs every 6 hours. This function checks whether there is a
newly finished gameweek in the database. Only if there is does the expensive
ingest + validate + load step run.

Returns False if:
  - No gameweeks have finished yet (first run, offseason)
  - The last finished gameweek was already processed last run
"""
import json
from pathlib import Path

from src.config import CONFIG

DB = CONFIG["paths"]["database"]
STATE_FILE = Path(__file__).resolve().parents[2] / ".github" / "refresh_state.json"


def has_new_finished_gameweek() -> bool:
    """True if there is a finished gameweek we have not yet processed."""
    try:
        import sqlite3
        import duckdb
        
        # Read last processed gameweek from state file
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text())
            last_processed = state.get("last_finished_gw")
        else:
            last_processed = None
        
        # Check database for latest finished gameweek
        if DB.suffix == ".duckdb":
            with duckdb.connect(str(DB), read_only=True) as conn:
                result = conn.execute(
                    "SELECT max(gameweek_id) FROM dim_gameweek WHERE finished"
                ).fetchall()
                latest_finished = result[0][0] if result and result[0][0] else None
        else:
            with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as conn:
                result = conn.execute(
                    "SELECT max(gameweek_id) FROM dim_gameweek WHERE finished"
                ).fetchone()
                latest_finished = result[0] if result and result[0] else None
        
        # No finished gameweeks yet
        if latest_finished is None:
            return False
        
        # New gameweek finished since last run
        if last_processed is None or latest_finished > last_processed:
            return True
        
        return False
    
    except Exception as e:
        print(f"Error checking gameweek state: {e}")
        return False  # Fail safely — skip refresh on error


def record_refresh(gw: int) -> None:
    """Record that we have processed this gameweek."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"last_finished_gw": gw}))


if __name__ == "__main__":
    import sys
    should_refresh = has_new_finished_gameweek()
    print(f"should_refresh={'true' if should_refresh else 'false'}")
    sys.exit(0)