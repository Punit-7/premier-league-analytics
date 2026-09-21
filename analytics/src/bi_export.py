"""Flat CSV exports that Power BI and Excel read. One file per table."""
import sqlite3

import pandas as pd

from src.config import CONFIG
from src.logging_setup import get_logger, stage

log = get_logger(__name__)

TABLES = ["dim_team", "dim_season", "dim_date", "dim_position",
          "dim_gameweek", "dim_player", "fact_match", "fact_player_fixture",
          "fact_team_fixture", "refresh_log"]

VIEWS = ["v_team_match", "v_player_season"]


def main() -> None:
    with stage(log, "bi_export"):
        out = CONFIG["paths"]["bi"]
        with sqlite3.connect(CONFIG["paths"]["database"]) as conn:
            for name in TABLES + VIEWS:
                df = pd.read_sql_query(f"SELECT * FROM {name}", conn)
                df.to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")
                log.info("exported %-22s %7d rows", name, len(df))
        log.info("exported %d tables to %s", len(TABLES), out)


if __name__ == "__main__":
    main()