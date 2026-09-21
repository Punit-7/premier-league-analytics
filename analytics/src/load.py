"""Create the database from schema.sql and load the star schema."""
import sqlite3

from src.config import CONFIG, ROOT
from src.model import build_all
from src.logging_setup import get_logger, stage

log = get_logger(__name__)

SCHEMA = ROOT / "sql" / "schema.sql"

LOAD_ORDER = ["dim_team", "dim_season", "dim_date", "dim_referee",
              "dim_position", "dim_gameweek", "dim_player",
              "fact_match", "fact_player_fixture", "fact_team_fixture"]

def main() -> None:
    with stage(log, "load"):
        tables = build_all()
        with sqlite3.connect(CONFIG["paths"]["database"]) as conn:
            conn.executescript(SCHEMA.read_text())
            conn.execute("PRAGMA foreign_keys = ON")
            for name in LOAD_ORDER:
                df = tables[name].copy()
                for col in df.select_dtypes(include=["bool", "boolean"]).columns:
                    df[col] = df[col].astype(int)
                for col in df.select_dtypes(include=["datetime64[ns, UTC]",
                                                     "datetime64[ns]"]).columns:
                    df[col] = df[col].astype(str)
                df.to_sql(name, conn, if_exists="append", index=False)
                log.info("loaded %-22s %7d rows", name, len(df))
            tables["refresh_log"].to_sql("refresh_log", conn,
                                         if_exists="append", index=False)
            violations = conn.execute("PRAGMA foreign_key_check").fetchall()
            if violations:
                raise RuntimeError(f"Foreign key violations: {violations[:5]}")
        log.info("built %s", CONFIG["paths"]["database"])


if __name__ == "__main__":
    main()
            
    