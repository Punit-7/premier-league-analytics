"""Create the database and load every table.

TODO: implement. See the build guide for this stage.
"""
from src.logging_setup import get_logger
from src import run_log

log=get_logger(__name__)

entries = run_log.read_all()

if entries:
    pd.DataFrame(entries).to_sql("pipeline_run", conn, if_exists="append",
                                 index= False\)
    log.info("Loaded %d pipeline run records"m len(entries))

def main() -> None:
    raise NotImplementedError("Not implemented yet.")


if __name__ == "__main__":
    main()
