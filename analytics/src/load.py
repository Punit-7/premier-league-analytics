"""Land the raw datasets into DuckDB. dbt reads these as sources and models
the star schema on top; nothing here does any transformation.
"""
from datetime import datetime, timezone

import duckdb
import pandas as pd

from src.config import CONFIG
from src.logging_setup import get_logger, stage

log = get_logger(__name__)

INTERIM = CONFIG["paths"]["interim"]
DB = CONFIG["paths"]["database"]

# raw table name -> interim parquet file it is landed from
RAW_TABLES = {
    "raw_matches": "matches_clean",
    "raw_players": "fpl_players",
    "raw_positions": "fpl_positions",
    "raw_gameweeks": "fpl_gameweeks",
    "raw_fixtures": "fpl_team_fixtures",
    "raw_player_fixture": "fpl_history",
}


def build_refresh_row(matches: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    live = matches[matches["is_current_season"]]
    return pd.DataFrame([{
        "refreshed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_matches": len(matches),
        "live_matches": len(live),
        "player_fixture_rows": len(history),
        "latest_gameweek": int(history["gameweek_id"].max()) if not history.empty else None,
        "latest_match_date": (live["match_date"].max().strftime("%Y-%m-%d")
                              if not live.empty else None),
    }])


def main() -> None:
    with stage(log, "load"):
        with duckdb.connect(str(DB)) as conn:
            for raw_name, parquet_name in RAW_TABLES.items():
                path = INTERIM / f"{parquet_name}.parquet"
                conn.execute(
                    f"CREATE OR REPLACE TABLE {raw_name} AS "
                    f"SELECT * FROM read_parquet($path)", {"path": str(path)})
                rows = conn.execute(f"SELECT count(*) FROM {raw_name}").fetchone()[0]
                log.info("landed %-22s %7d rows", raw_name, rows)

            matches = pd.read_parquet(INTERIM / "matches_clean.parquet")
            history = pd.read_parquet(INTERIM / "fpl_history.parquet")
            refresh_row = build_refresh_row(matches, history)
            # Never replaced: one row per refresh accumulates as history.
            conn.execute("CREATE TABLE IF NOT EXISTS refresh_log AS "
                         "SELECT * FROM refresh_row LIMIT 0")
            conn.execute("INSERT INTO refresh_log SELECT * FROM refresh_row")
            log.info("landed %-22s %7d rows", "refresh_log", len(refresh_row))
        log.info("built %s", DB)


if __name__ == "__main__":
    main()
