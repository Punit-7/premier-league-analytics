"""Event detection: has a new gameweek finished since the last refresh?

The workflow runs every 6 hours. The check asks the FPL API for the latest
finished gameweek and compares it with the one recorded in
.github/refresh_state.json. Only if it is newer does the expensive
ingest + validate + load step run; that job then records the gameweek.

The check reads the API, not epl.duckdb: the database only changes when a
refresh runs, so it can never reveal a gameweek that finished since.

Prints nothing but key=value lines on stdout, because the workflow appends
stdout to $GITHUB_OUTPUT. Diagnostics go to stderr.
"""
import argparse
import json
import sys
from pathlib import Path

import requests

from src.config import CONFIG

BASE = CONFIG["fpl_source"]["base_url"]
STATE_FILE = Path(__file__).resolve().parents[1] / ".github" / "refresh_state.json"
HEADERS = {"User-Agent": "pl-analytics-portfolio/1.0 (+https://github.com/Punit-7/premier-league-analytics)"}


def latest_finished_gameweek() -> int | None:
    """Highest gameweek FPL has finished and finalised (bonus points applied)."""
    r = requests.get(f"{BASE}/bootstrap-static/", headers=HEADERS, timeout=30)
    r.raise_for_status()
    done = [e["id"] for e in r.json()["events"] if e["finished"] and e["data_checked"]]
    return max(done, default=None)


def last_processed_gameweek() -> int | None:
    if not STATE_FILE.exists():
        return None
    return json.loads(STATE_FILE.read_text()).get("last_finished_gw")


def has_new_finished_gameweek(latest: int | None) -> bool:
    """True if `latest` is a finished gameweek we have not yet processed."""
    if latest is None:          # offseason, or before gameweek 1 ends
        return False
    last = last_processed_gameweek()
    return last is None or latest > last


def record_refresh(gw: int) -> None:
    """Record that we have processed this gameweek."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"last_finished_gw": gw}) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", type=int, metavar="GW",
                    help="record GW as processed instead of checking")
    args = ap.parse_args()

    if args.record is not None:
        record_refresh(args.record)
        print(f"recorded gameweek {args.record}", file=sys.stderr)
        return 0

    try:
        latest = latest_finished_gameweek()
    except Exception as e:      # fail safe: skip this refresh, try again in 6 hours
        print(f"Error checking gameweek state: {e}", file=sys.stderr)
        latest = None
    should = has_new_finished_gameweek(latest)
    print(f"latest finished={latest}, last processed={last_processed_gameweek()}", file=sys.stderr)
    print(f"should_refresh={str(should).lower()}")
    print(f"gameweek={latest or ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
