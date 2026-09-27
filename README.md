# Premier League Analytics · Live Season & FPL Tracker

A live Premier League warehouse that answers one question every gameweek: **which Fantasy Premier League players are worth their price this week?**

Live app: TODO

## The question it answers

FPL managers have a £100m budget and 15 squad places. Price is the obvious guide, but it is a weak one: so far this season, price explains only about 15% of the variation in points (see [Key findings](#key-findings)). This project measures value directly. It ranks players by points per million, current form, fixture difficulty and ownership, alongside the live league table and eleven seasons of match history for context.

## Data sources

| Source | What it provides | Coverage |
|---|---|---|
| [football-data.co.uk](https://www.football-data.co.uk) (`E0` CSVs) | Match results, half-time scores, shots, fouls, corners, cards, referee | 2015/16 to the live 2026/27 season |
| [FPL API](https://fantasy.premierleague.com/api) | Players, prices, ownership, positions, gameweeks, fixtures with difficulty, per-fixture player history | Live season only |

The seasons and endpoints are set in `config.yaml`. Raw responses are cached under `data/raw/` and never edited. The two sources name clubs differently ("Man United" and "Man Utd"), so both are mapped to one canonical name in `src/team_names.py`, and an unmapped name stops the pipeline.

## Architecture

```
football-data CSVs ─┐                                        ┌─ Streamlit app
                    ├─ ingest ─ clean ─ quality ─ load ─ dbt ┼─ Power BI report   (via CSV export)
FPL API ────────────┘   src/     src/     src/     src/      └─ Excel workbook    (via CSV export)
```

1. **Ingest** (`src/ingest_matches.py`, `src/ingest_fpl.py`). Downloads the raw files. A refresh re-fetches only players whose season totals changed, which cuts a sweep of about 700 calls down to a handful.
2. **Clean** (`src/clean_matches.py`, `src/clean_players.py`). Turns the raw files into typed Parquet in `data/interim/`.
3. **Quality** (`src/quality.py`). Runs the data contracts and stops on any failure.
4. **Load** (`src/load.py`). Lands the cleaned data in DuckDB as `raw_*` tables, without transforming it.
5. **dbt**. Builds the models: `staging` views, `marts` star-schema tables, and `analytics` reporting tables.
6. **Export** (`src/bi_export.py`). Writes one CSV per table to `data/powerbi/` for Power BI and Excel.

The warehouse is one DuckDB file, `data/processed/epl.duckdb`. It is committed, so the app and reports work straight after a clone.

### The star schema

There are two core fact tables, one per source:

| Fact | Grain | Rows* |
|---|---|---|
| `fact_match` | One row per completed fixture, all seasons | 4,230 |
| `fact_player_fixture` | One row per player per fixture. A double gameweek gives two rows. | 3,216 |

The player fact is deliberately kept at fixture grain, not gameweek grain, because a per-gameweek grain would silently lose one fixture of a double gameweek.

`fact_team_fixture` holds one row per team per FPL fixture, played and upcoming (760 rows). It carries FPL's fixture difficulty rating.

- **Dimensions:** `dim_team`, `dim_season`, `dim_date` (contiguous, so Power BI can mark it as a date table), `dim_gameweek`, `dim_player`, `dim_position` and `dim_referee`.
- **Reporting tables:** `team_match`, `player_season` and `player_value`.
- **Load history:** `refresh_log` records every load.

\*Row counts as of gameweek 5, refreshed 23 September 2026. Every column, type, null count and observed range is in [`docs/data_dictionary.md`](docs/data_dictionary.md).

### Analysis queries

Ten standalone queries in [`sql/analysis/`](sql/analysis) run against the marts:

| # | Question |
|---|---|
| 01 | Current standings, ranked the way the league ranks them |
| 02 | Which players return the most points per pound of budget? |
| 03 | Who is in form right now, not who has been good all season? |
| 04 | Whose fixtures get easier soon? |
| 05 | High returns at low ownership: the differential search |
| 06 | The live title race as a running total |
| 07 | Longest unbeaten streak per team per season (gaps and islands) |
| 08 | What does each position actually return, and at what price? |
| 09 | Is 2026/27 unusual, or is this just a small sample? |
| 10 | Who earns the most bonus points, and what share of their total they make up |

## How to run from a clean clone

You need Python 3.12 (the version CI uses) and `make`. On Windows, `winget install ezwinports.make` provides `make`.

```bash
git clone <this-repo-url>
cd premier-league-analytics
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # exact versions: requirements.lock.txt
dbt deps                           # installs dbt_utils
```

**Quick look (no rebuild).** The warehouse is committed:

```bash
make app                           # streamlit run app/dashboard.py
```

**Full rebuild.** This downloads every source and rebuilds the warehouse:

```bash
make all      # ingest → clean → quality → load + dbt build → export → pytest
```

Other targets:

| Target | What it runs |
|---|---|
| `make refresh` | Live-season-only rebuild: fetches the current season and changed FPL players, then runs clean, quality, load, `dbt build` and export |
| `make quality` | The Python data contracts only |
| `make test` | `pytest -v` |

Every stage writes to `logs/`, grouped by one run id per `make` invocation.

## The three front ends

All three read the same warehouse, so they cannot disagree.

### 1. Streamlit app — `app/dashboard.py`

This is the weekly decision tool. It reads DuckDB read-only and computes nothing itself. It has four sections:
- **Value: points against price.** A bubble chart where bubble size is ownership and the dashed line is the points expected at that price.
- **Best value per million.**
- **Easiest fixtures, next 5 gameweeks.**
- **Player detail.** Points per fixture for one player, with the opponent and home or away.

Run it with `make app`. The theme is in `.streamlit/config.toml`, and the app's hosting dependencies are in `app/requirements.txt`.

### 2. Power BI report — `powerbi/pl-analytics.pbix`

This is a two-page report (a main page and a player detail page) built on the star schema. It uses the theme in `powerbi/pl-theme.json`, and a PDF export is in `powerbi/pl-analytics.pdf`.

The report reads the CSV export in `data/powerbi/`. The path is stored as a parameter, so point it at your clone:

1. Open `powerbi/pl-analytics.pbix` in Power BI Desktop.
2. Go to Home → Transform data → Manage Parameters.
3. Set `DataPath` to your clone's `data/powerbi` folder.
4. Choose Close & Apply.

The CSVs are committed, so you don't need to rebuild anything first.

### 3. Excel briefing workbook — `excel/pl_Excel_report.xlsx`

This is a refreshable briefing with six sheets: **README, Briefing, Fixture Ticker, Watchlist, Data, Refresh**. It covers player value, fixture difficulty and a personal watchlist.
- The only hand-typed input is the player names in column A of the Watchlist sheet.
- All shaping happens in Power Query, not in cell formulas.
- It reads the same `data/powerbi/` CSVs through a `DataPath` parameter. To change it, go to Data → Get Data → Launch Power Query Editor → Manage Parameters.
- It needs Microsoft 365, build 2608 or later. The Watchlist uses `LET`, `FILTER`, `HSTACK`, `BYROW` and `MAP`, so older Excel shows `#NAME?`.

## Key findings

These come from [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb) and are **as of gameweek 5** (refreshed 23 September 2026, 50 matches played). They will change every week.

1. **Price explains only about 15% of the variance in points.**
   - Price and points correlate at r = 0.39 (r² = 0.15).
   - The six largest positive residuals, meaning players who beat their price, are Groß, Bogle, Tarkowski, De Cuyper, Schade and Tzolakis.
   - *So what:* screen on residual, not on price.
2. **56% of the player pool has played under 90 minutes.**
   - That is 371 of 667 players: 67% of goalkeepers, 66% of forwards, 57% of midfielders and 46% of defenders.
   - *So what:* every per-value metric needs a minutes floor. The SQL queries use 270 minutes and the notebook charts use 180.
3. **Bonus points system score (bps) tracks points far better than price.**
   - bps correlates with total points at r = 0.89, against 0.39 for price. ICT index (0.67), goals (0.63) and minutes (0.56) all beat price too.
   - *Caveat:* bps and points are scored from the same match events, so this is closer to a restatement than an independent predictor.
4. **Fixture difficulty clusters.**
   - Average FPL difficulty over the next five gameweeks runs from 2.4 (Fulham, Coventry City) to 3.6 (Leeds United, Brighton & Hove Albion).
   - *So what:* use it as one input, not as a ranking.
5. **The live season is not yet distinguishable from normal.**
   - Goals per match is 2.82, against an eleven-season mean of 2.82.
   - The rough 95% interval (2.29 to 3.35) contains both the baseline and 2023/24's outlier of 3.28, so there is nothing to act on yet.

## Data quality

The project has two independent quality suites plus unit tests.

**1. Python data contracts** (`src/quality.py`). These run on the cleaned data before anything is loaded, and any failure stops the pipeline. There are 13 checks in four groups, because completed-season rules cannot apply to a season still in progress:

| Group | Checks |
|---|---|
| All matches | No nulls in required columns; the natural key is unique; the result agrees with the scoreline; no future-dated matches |
| Completed seasons | 380 matches per season; every team plays 38 |
| Live season | 0 to 380 matches; fixture spread between teams within a configured tolerance |
| Players | Prices between £3.0m and £20.0m; enough players per position for a legal squad; minutes between 0 and 120; one row per player per fixture; every FPL club appears in the match data |

**2. dbt tests** (`models/**/*.yml`, `tests/*.sql`). These run on the built warehouse as part of `dbt build`:
- Generic tests: `not_null`, `relationships`, `accepted_values`, and the `dbt_utils` tests `accepted_range` and `unique_combination_of_columns`.
- Two singular tests: `dim_date` has no gaps, and no gameweek is missing from the player fact.

**3. Unit tests** (`tests/test_*.py`, 10 tests). These cover cleaning (club-name mapping, derived points, day-first dates, rejecting unplayed and duplicate fixtures) and the quality checks (bad price conversion, double gameweeks, minutes bounds).

The source quirks behind these rules are recorded in [`docs/known_issues.md`](docs/known_issues.md).

## Automation

Two GitHub Actions workflows live in `.github/workflows/`:

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | Every push and pull request | Installs requirements, runs `ruff check src tests app` and `pytest -v` |
| `refresh.yml` | Every 6 hours (`0 */6 * * *`), or manually | See below |

`refresh.yml` runs in two jobs:
1. **Check.** `src/refresh_check.py` looks for a finished gameweek that has not been processed yet.
2. **Refresh.** This job runs only if the check finds one. It ingests, cleans, runs the quality contracts, loads and exports, then commits the updated `epl.duckdb` and `data/powerbi/` CSVs back to the repository.

The FPL raw cache is kept between runs with `actions/cache`.

## Known limitations

**Data**
- **Everything player-level covers one partial season.** Treat it as descriptive, not predictive. The findings above rest on five gameweeks.
- **FPL's API has no historical seasons,** so there is no multi-season player comparison.
- **Fixture difficulty is FPL's own 1 to 5 rating.** It is set before the season and does not know about injuries or form.
- **Two baseline seasons were played without crowds.** 2019/20 was partly and 2020/21 almost entirely behind closed doors. Both are flagged in `dim_season` but are not controlled for in the analysis.
- **Coventry City and Hull City have no Premier League history** in the baseline, so prior-season comparisons are undefined for them.

**Front ends**
- **The Power BI and Excel `DataPath` parameters are absolute paths** and must be set once per machine.

**Automation**
- **The scheduled refresh does not run `dbt build`.** It loads the `raw_*` tables and exports, while `make refresh` rebuilds the dbt models locally.
- **The "already processed" gameweek is never recorded.** `refresh_check.record_refresh()` is never called and its state file is not committed, so once any gameweek has finished, every scheduled check triggers a refresh.

## Project layout

```
.github/workflows/   ci.yml, refresh.yml
app/                 Streamlit app
data/
  processed/         epl.duckdb, the warehouse (committed)
  powerbi/           CSV export for Power BI and Excel (committed)
  raw/, interim/     local cache, regenerated by the pipeline
docs/                data dictionary, known issues
excel/               briefing workbook
models/              dbt: staging, marts, analytics
notebooks/           00_exploration, 01_eda (findings)
powerbi/             .pbix, PDF export, theme
sql/analysis/        the ten analysis queries
src/                 pipeline stages
tests/               pytest unit tests and dbt singular tests
config.yaml          seasons, sources, paths, expectations
dbt_project.yml, profiles.yml, packages.yml
Makefile
```
