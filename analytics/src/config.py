"""Load config.yaml and resolve paths.

TODO: implement. See the build guide for this stage.
"""
from src.logging_setup import get_logger
from pathlib import Path
import yaml

log=get_logger(__name__)

ROOT = Path(__file__).resolve().parents[1]


def load_config(path: Path | None= None) -> dict:
    with open(path or ROOT / "config.yaml") as f:
        
        cfg = yaml.safe_load(f)
    
    cfg["paths"] = {k: ROOT / v for k,v in cfg["paths"].items()}
    for key in ("raw","fpl_raw","interim", "processed", "bi"):
        cfg["paths"][key].mkdir(parents=True, exist_ok=True)
    cfg["all_seasons"] = cfg["historical_seasons"] + [cfg["current_season"]]
    return cfg


CONFIG = load_config()