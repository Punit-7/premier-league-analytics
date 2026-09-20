"""Create the premier-league-analytics scaffolding. Idempotent: never overwrites existing files.

    python scripts/bootstrap.py            # create anything missing
    python scripts/bootstrap.py --dry-run  # show what would be created
    python scripts/bootstrap.py --force    # overwrite boilerplate (not stubs)
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# print(f"Bootstrapping premier-league-analytics in {ROOT}") 

DIRS = [
    "packages","modelling","serving","assistant",
    ".github/workflows",
    "analytics/src","analytics/tests","analytics/app",
    "analytics/sql/analysis","analytics/notebooks","analytics/docs",
    "analytics/powerbi","analytics/excel","analytics/logs",
    "analytics/.streamlit","analytics/data/raw","analytics/data/interim",
    "analytics/data/processed","analytics/data/powerbi"
    ]

# Directories that must survive a clone even when empty.

KEEP = [
    "analytics/data/raw","analytics/data/interim",
    "analytics/data/processed","analytics/data/powerbi",
    "analytics/logs", "analytics/docs",
    "packages","modelling","serving","assistant"
    ]

# Module stubs: path -> (one-line docstring, has a main() entry point)
STUBS = {
    "analytics/src/config.py":         ("Load config.yaml and resolve paths.", False),
    "analytics/src/logging_setup.py":  ("Central logging configuration.", False),
    "analytics/src/run_log.py":        ("Append structured stage records to logs/runs.jsonl.", False),
    "analytics/src/ingest_matches.py": ("Fetch match-result CSVs. Raw is immutable.", True),
    "analytics/src/ingest_fpl.py":     ("Fetch FPL bootstrap, fixtures and player histories.", True),
    "analytics/src/profile.py":        ("Profile both sources before transforming them.", True),
    "analytics/src/team_names.py":     ("Canonical club names for both sources.", False),
    "analytics/src/clean_matches.py":  ("Raw match CSVs to one validated dataset.", True),
    "analytics/src/clean_players.py":  ("FPL JSON to tidy player tables.", True),
    "analytics/src/model.py":          ("Build star-schema dimensions and facts.", False),
    "analytics/src/load.py":           ("Create the database and load every table.", True),
    "analytics/src/quality.py":        ("Data contracts. Fails loudly on bad input.", True),
    "analytics/src/bi_export.py":      ("Export the star schema as CSV for Power BI and Excel.", True),
    "analytics/app/style.py":          ("Design tokens and injected CSS for the app.", False),
    "analytics/app/dashboard.py":      ("Streamlit front end. Reads the database, computes nothing.", False),
}

PACKAGES = ["analytics/src/__init__.py", "analytics/tests/__init__.py"]

GITIGNORE = """\
.venv/
__pycache__/
*.pyc
*.ipynb_checkpoints/
.DS_Store
.env

# Regenerable inputs
analytics/data/raw/
analytics/data/interim/

# Logs are per-run and local; the JSONL record is loaded into the database
analytics/logs/*.log
analytics/logs/runs.jsonl

# Published on purpose by the refresh job
!analytics/data/processed/epl.db
!analytics/data/powerbi/
"""

REQUIREMENTS = """\
pandas==2.2.3
numpy==2.1.3
pyarrow==18.1.0
requests==2.32.3
streamlit==1.40.2
plotly==5.24.1
matplotlib==3.9.3
seaborn==0.13.2
jupyterlab==4.3.4
pytest==8.3.4
pyYAML==6.0.2
ruff==0.8.4    
"""

STREAMLIT_THEME = """\
[theme]
base = "light"
primaryColor = "#1F6A4A"
backgroundColor = "#FAFAF8"
secondaryBackgroundColor = "#F0F2ED"
textColor = "#16191A"
font = "sans serif"

[server]
headless = true
"""

ROOT_README = """\
# Premier League Analytics

A Premier League analytics platform. One ingest pipeline and one data contract,
feeding four independent surfaces.

| Surface | What it is | Live |
|---|---|---|
| [analytics/](analytics)  | Star-schema warehouse, SQL, Power BI, live dashboard | TODO |
| [modelling/](modelling)  | FPL points model and squad optimiser                 | TODO |
| [serving/](serving)      | The model as a tested, monitored API                 | TODO |
| [assistant/](assistant)  | Retrieval-augmented assistant over the season corpus | TODO |

Scaffolded with `python scripts/bootstrap.py`.
"""

def stub_body(docstring: str, has_main: bool) -> str:
    """Return a stub body for a module with the given docstring and main() entry point."""
    body = f'"""{docstring}\n\nTODO: implement. See the build guide for this stage.\n"""\n'
    body += "from src.logging_setup import get_logger\n\nlog=get_logger(__name__)\n"
    
    if has_main:
        body += (
            '\n\ndef main() -> None:\n'
            '    raise NotImplementedError("Not implemented yet.")\n'
            '\n\nif __name__ == "__main__":\n'
            '    main()\n'
        )
    return body


def write(path: Path, content: str,*,dry: bool, force: bool, protected: bool = False) -> str:
    """Return one of: created, skipped, overwritten."""
    if path.exists():
        if not force or protected:
            return "skipped"
        action = "overwritten"
    
    else:
        action = "created"
    
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return action


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", 
                    help="overwrite boilerplate; module stubs are always protected")
    
    args = ap.parse_args()
    
    tally = {"created": 0, "skipped": 0, "overwritten": 0}
    
    def record(label: str, action: str) -> None:
        tally[action] += 1
        symbol = {"created": "+", "skipped": "=", "overwritten": "~"}[action]
        print(f"{symbol} {label} ({action})")
        
    print("Directories")
    for d in DIRS:
        p = ROOT / d
        existed = p.exists()
        if not args.dry_run:
            p.mkdir(parents=True, exist_ok=True)
        record(d+"/", "skipped" if existed else "created")
    
    print("\nKeep markers")
    for d in KEEP:
        record(f"{d}/.gitkeep",write(ROOT / d / ".gitkeep", "", dry = args.dry_run, force=False))
    
    print("\nBoilerplate")
    boilerplate = {
        ".gitignore": GITIGNORE,
        "README.md": ROOT_README,
        "analytics/requirements.txt": REQUIREMENTS,
        "analytics/.streamlit/config.toml": STREAMLIT_THEME
    }
    
    for rel,content in boilerplate.items():
        record(rel, write(ROOT / rel, content, dry=args.dry_run, force=args.force))
        
    print("\nModule stubs (never overwritten)")
    for rel, (doc, has_main) in STUBS.items():
        record(rel, write(ROOT / rel, 
                          stub_body(doc, has_main), dry=args.dry_run, force=args.force, protected=True))
    
    print(f"\n{tally['created']} created, {tally['skipped']} skipped, {tally['overwritten']} overwritten.")
    
    if args.dry_run:
        print("Dry run - nothing was written.")
    return 0

if __name__ == "__main__":
    sys.exit(main())