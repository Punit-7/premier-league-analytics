"""Fetch raw season files. Completed seasons cached; the live one always re-fetched."""
import argparse
import hashlib
import json
from datetime import datetime, timezone

import requests

from src.config import CONFIG
from src.logging_setup import get_logger, stage

log = get_logger(__name__)

MANIFEST = CONFIG["paths"]["raw"] / "match_manifest.json"

def read_manifest() -> dict:
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}

def fetch(season: str) -> bytes:
    url = (f"{CONFIG['match_source']['base_url']}/{season}"
           f"/{CONFIG['match_source']['division']}.csv")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content

def store(season: str, payload: bytes, manifest: dict) -> bool:
    dest = CONFIG["paths"]["raw"] / f"E0_{season}.csv"
    digest = hashlib.sha256(payload).hexdigest()
    changed = digest != manifest.get(season,{}).get("sha256")
    dest.write_bytes(payload)
    manifest[season] = {
        "season": season, "file": dest.name, "bytes": len(payload),
        "sha256": digest, "rows": payload.count(b"\n") - 1,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    return changed

def main() -> None:
    with stage(log,"ingest_matches"):
        ap = argparse.ArgumentParser()
        ap.add_argument("--current-only", action="store_true")
        ap.add_argument("--force", action="store_true")
        args = ap.parse_args()
        
        manifest = read_manifest()
        
        if not args.current_only:
            for season in CONFIG["historical_seasons"]:
                path = CONFIG["paths"]["raw"] / f"E0_{season}.csv"
                if path.exists() and season in manifest and not args.force:
                    log.debug("season %s cached (%s rows)",
                              season, manifest[season]["rows"])
                    continue
                store(season, fetch(season), manifest)
                log.info("season %s downloaded (%s rows)",
                         season, manifest[season]["rows"])
        
        current  = CONFIG["current_season"]
        changed = store(current, fetch(current), manifest)
        log.info("live season %s: %s matches [%s]", current,
                 manifest[current]["rows"],
                 "new data" if changed else "unchanged")

        MANIFEST.write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
