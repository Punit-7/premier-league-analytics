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


def main() -> None:
    started = time.perf_counter()
    rows = None`
    try:`
        with stage(log, "ingest_matches"):
            manifest = read_manifest()
            cached = downloaded = 0

            for season in CONFIG["historical_seasons"]:
                if already_cached(season, manifest):
                    log.debug("season %s cached", season)
                    cached += 1
                    continue
                store(season, fetch(season), manifest)
                log.info("season %s downloaded", season)
                downloaded += 1

            live = CONFIG["current_season"]
            changed = store(live, fetch(live), manifest)
            rows = manifest[live]["rows"]
            log.info("live season %s: %s matches (%s)", live, rows,
                     "new data" if changed else "unchanged")
            log.info("%d cached, %d downloaded", cached, downloaded)

            MANIFEST.write_text(json.dumps(manifest, indent=2))
    except Exception as exc:
        run_log.record("ingest_matches", "failed",
                       time.perf_counter() - started, message=str(exc))
        raise
    else:
        run_log.record("ingest_matches", "ok",
                       time.perf_counter() - started, rows=rows)


if __name__ == "__main__":
    main()
