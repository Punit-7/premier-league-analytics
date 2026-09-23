"""Flat CSV exports that Power BI and Excel read. One file per table.

Reads from the dbt-built DuckDB marts, not from Python — the marts are the
one place the star schema is defined since stage 11.
"""
import duckdb
import pandas as pd

from src.config import CONFIG
from src.logging_setup import get_logger, stage

log = get_logger(__name__)

TABLES = ["dim_team", "dim_season", "dim_date", "dim_position",
          "dim_gameweek", "dim_player", "fact_match", "fact_player_fixture",
          "fact_team_fixture", "team_match", "player_season", "refresh_log"]


def main() -> None:
    with stage(log, "bi_export"):
        out = CONFIG["paths"]["bi"]
        with duckdb.connect(str(CONFIG["paths"]["database"]), read_only=True) as conn:
            for name in TABLES:
                df = conn.execute(f"SELECT * FROM {name}").df()
                df.to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")
                log.info("exported %-22s %7d rows", name, len(df))
        log.info("exported %d tables to %s", len(TABLES), out)


if __name__ == "__main__":
    main()
