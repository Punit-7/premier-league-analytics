"""Central logging configuration.

Console  — terse, for interactive work
pipeline.log — rotating, the last few megabytes of everything
run_{RUN_ID}.log — one file per pipeline run, so a single 6am refresh is readable

RUN_ID comes from the environment when CI sets it, so every stage in one
scheduled run writes to the same run file. Locally it is a UTC timestamp.
"""

import logging
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"

RUN_ID = os.environ.get("PL_RUN_ID") or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

FILE_FORMAT = "%(asctime)s %(levelname)-7s %(name)-18s %(message)s"
CONSOLE_FORMAT = "%(levelname)-7s %(message)s"

_configured = False

def _configure() -> None:
    global _configured
    
    if _configured:
        return
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logger= logging.getLogger("pipeline")
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
    logger.propagate = False
    logger.handlers.clear()
    
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(CONSOLE_FORMAT))
    logger.addHandler(console)
    
    rolling = RotatingFileHandler(LOG_DIR / "pipeline.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    rolling.setFormatter(logging.Formatter(FILE_FORMAT))
    logger.addHandler(rolling)
    
    per_run = logging.FileHandler(LOG_DIR / f"run_{RUN_ID}.log", encoding="utf-8")
    per_run.setFormatter(logging.Formatter(FILE_FORMAT))
    logger.addHandler(per_run)
    
    _configured = True
    
def get_logger(name: str) -> logging.Logger:
    """get_logger(__name__) in every module. Child of one configured parent."""
    _configure()
    return logging.getLogger(f"pipeline.{name.rsplit('.', 1)[-1]}")

@contextmanager
def stage(log: logging.Logger, name: str):
    """Time a pipeline stage and guarantee the failure is recorded.

    Without this, an exception inside a stage prints a traceback to stderr and
    leaves nothing in the log file — which is exactly the case you need
    evidence for when a scheduled run fails overnight.
    """

    started = time.perf_counter()
    log.info("START %s", name)

    try:
        yield
    except Exception:
        log.exception("FAILED %s after %.1fs", name, time.perf_counter() - started)
        raise
    else:
        log.info("DONE %s after %.1fs", name, time.perf_counter() - started)
        
