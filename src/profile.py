"""Profile both sources: what columns exist where, and how complete they are."""
import json

import pandas as pd

from src.config import CONFIG
from src.logging_setup import get_logger, stage

log = get_logger(__name__)

def read_raw_match(season: str) -> pd.DataFrame:
    path = CONFIG["paths"]["raw"] / f"E0_{season}.csv"
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(path,encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path}")


def read_fpl(name: str):
    return json.loads((CONFIG["paths"]["fpl_raw"] / f"{name}.json").read_text())

def main() -> None:
    with stage(log, "profile"):
        presence: dict[str,list[str]] = {}
        for season in CONFIG["all_seasons"]:
            df = read_raw_match(season)
            tag = " (live)" if season == CONFIG["current_season"] else ""
            log.info("%s%s: %4d rows x %3d cols",
                     season, tag, df.shape[0], df.shape[1])
            for col in df.columns:
                presence.setdefault(col, []).append(season)

        total = len(CONFIG["all_seasons"])
        stable = sorted(c for c, s in presence.items() if len(s) == total)
        log.info("stable match columns (%d): %s", len(stable), ", ".join(stable))

        boot = read_fpl("bootstrap")
        log.info("FPL: %d players, %d teams",
                 len(boot["elements"]), len(boot["teams"]))
        log.info("positions: %s", {t["id"]: t["singular_name_short"]
                                   for t in boot["element_types"]})
        log.info("squad limits: %s", {t["singular_name_short"]:
                                      (t["squad_min_play"], t["squad_max_play"],
                                       t["squad_select"])
                                      for t in boot["element_types"]})
        sample = boot["elements"][0]
        log.debug("player fields (%d): %s", len(sample), ", ".join(sorted(sample)))


if __name__ == "__main__":
    main()