"""Fetch FPL data: bootstrap, fixtures, and per-player histories.

Every response is cached to disk as raw JSON. On refresh we only re-fetch
players whose season totals changed, which cuts a ~700-call sweep to a handful.
"""
import argparse
import json
import time
from datetime import datetime, timezone

import requests

from src.config import CONFIG
from src.logging_setup import get_logger, stage

log = get_logger(__name__)

BASE = CONFIG["fpl_source"]["base_url"]
DELAY = CONFIG["fpl_source"]["request_delay_seconds"]
RAW = CONFIG["paths"]["fpl_raw"]
HEADERS = {"User-Agent": "pl-analytics-portfolio/1.0 (+https://github.com/Punit-7/premier-league-analytics)"}

def get(path: str) -> dict:
    r = requests.get(f"{BASE}/{path}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def save(name: str, payload) -> None:
    (RAW / f"{name}.json").write_text(json.dumps(payload))
    
def load(name: str):
    path = RAW / f"{name}.json"
    return json.loads(path.read_text()) if path.exists() else None

def fetch_bootstrap() -> dict:
    data = get("bootstrap-static/")
    save("bootstrap", data)
    log.info("bootstrap: %d players, %d teams, %d gameweeks",
             len(data["elements"]), len(data["teams"]), len(data["events"]))
    return data
    
def fetch_fixtures() -> list:
    data = get("fixtures/")
    save("fixtures", data)
    played = sum(1 for f in data if f.get("finished"))
    log.info("fixtures: %d total, %d played", len(data), played)
    return data

def players_needing_refresh(elements: list) -> list[int]:
    """Only re-fetch a player whose season points or minutes moved."""
    previous = load("player_totals") or {}
    stale, totals = [], {}
    for e in elements:
        key = str(e["id"])
        signature = f"{e['total_points']}:{e['minutes']}"
        totals[key] = signature
        if previous.get(key) != signature or not (RAW / f"player_{key}.json").exists():
            stale.append(e["id"])
    save("player_totals", totals)
    return stale


def fetch_player_histories(elements: list, refresh_only: bool) -> None:
    targets = players_needing_refresh(elements) if refresh_only \
        else [e["id"] for e in elements]
    log.info("fetching %d of %d player histories (~%.0fs)",
             len(targets), len(elements), len(targets) * DELAY)
    for n, pid in enumerate(targets, 1):
        save(f"player_{pid}", get(f"element-summary/{pid}/"))
        time.sleep(DELAY)
        if n % 100 == 0:
            log.debug("swept %d/%d", n, len(targets))


def main() -> None:
    with stage(log, "ingest_fpl"):
        ap = argparse.ArgumentParser()
        ap.add_argument("--refresh", action="store_true",
                        help="only re-fetch players whose totals changed")
        args = ap.parse_args()

        bootstrap = fetch_bootstrap()
        fetch_fixtures()
        fetch_player_histories(bootstrap["elements"], refresh_only=args.refresh)

        save("fpl_manifest", {
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "players": len(bootstrap["elements"]),
            "current_gameweek": next(
                (e["id"] for e in bootstrap["events"] if e["is_current"]), None
            ),
        })
        log.info("sweep complete")

if __name__ == "__main__":
    main()
