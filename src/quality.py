"""Data contracts. Completed-season rules, live-season rules, player rules."""
from dataclasses import dataclass

import pandas as pd

from src.config import CONFIG
from src.logging_setup import get_logger, stage

log = get_logger(__name__)


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


# --- any data -------------------------------------------------------------

def check_no_nulls(df, columns) -> CheckResult:
    nulls = {c: int(df[c].isna().sum()) for c in columns if df[c].isna().any()}
    return CheckResult("no nulls in required columns", not nulls,
                       "clean" if not nulls else f"nulls: {nulls}")


def check_unique_key(df, key) -> CheckResult:
    dupes = int(df.duplicated(subset=key).sum())
    return CheckResult("natural key is unique", dupes == 0, f"{dupes} duplicates")


def check_result_matches_goals(df) -> CheckResult:
    expected = df.apply(
        lambda r: "H" if r.ft_home_goals > r.ft_away_goals
        else ("A" if r.ft_home_goals < r.ft_away_goals else "D"), axis=1)
    bad = int((expected != df["ft_result"]).sum())
    return CheckResult("result agrees with scoreline", bad == 0, f"{bad} disagree")


def check_no_future_matches(df) -> CheckResult:
    n = int((df["match_date"] > pd.Timestamp.now()).sum())
    return CheckResult("no future-dated matches", n == 0, f"{n} rows")


# --- completed seasons only ----------------------------------------------

def check_season_completeness(df) -> CheckResult:
    expected = CONFIG["expectations"]["matches_per_completed_season"]
    counts = df.groupby("season_code").size()
    wrong = counts[counts != expected].to_dict()
    return CheckResult(f"completed seasons have {expected} matches", not wrong,
                       "all complete" if not wrong else f"off: {wrong}")


def check_each_team_plays_38(df) -> CheckResult:
    expected = CONFIG["expectations"]["matches_per_team_per_season"]
    long = pd.concat([
        df[["season_code", "home_team"]].rename(columns={"home_team": "team"}),
        df[["season_code", "away_team"]].rename(columns={"away_team": "team"}),
    ])
    wrong = long.groupby(["season_code", "team"]).size().pipe(
        lambda s: s[s != expected])
    return CheckResult(f"every team plays {expected}", wrong.empty,
                       "balanced" if wrong.empty else f"{len(wrong)} off")


# --- live season ----------------------------------------------------------

def check_live_within_bounds(df) -> CheckResult:
    cap = CONFIG["expectations"]["matches_per_completed_season"]
    return CheckResult("live season within 0..380", 0 <= len(df) <= cap,
                       f"{len(df)} matches")


def check_live_fixture_spread(df) -> CheckResult:
    allowed = CONFIG["expectations"]["max_matches_played_spread"]
    counts = pd.concat([df["home_team"], df["away_team"]]).value_counts()
    if counts.empty:
        return CheckResult("fixture spread within tolerance", True, "no matches yet")
    spread = int(counts.max() - counts.min())
    return CheckResult("fixture spread within tolerance", spread <= allowed,
                       f"spread {spread}, allowed {allowed}")


# --- player data ----------------------------------------------------------

def check_prices_plausible(players) -> CheckResult:
    bad = int(((players["price_m"] < 3.0) | (players["price_m"] > 20.0)).sum())
    return CheckResult("player prices between 3.0 and 20.0", bad == 0,
                       f"{bad} implausible")


def check_squad_size_is_reachable(players, positions) -> CheckResult:
    """You must be able to field a legal squad from the players we loaded."""
    needed = dict(zip(positions["position_id"], positions["squad_select"]))
    have = players.groupby("position_id").size().to_dict()
    short = {p: n for p, n in needed.items() if have.get(p, 0) < n}
    return CheckResult("enough players per position for a legal squad",
                       not short, "ok" if not short else f"short: {short}")


def check_minutes_bounded(history) -> CheckResult:
    bad = int(((history["minutes"] < 0) | (history["minutes"] > 120)).sum())
    return CheckResult("minutes between 0 and 120", bad == 0, f"{bad} outside")


def check_player_fixture_unique(history) -> CheckResult:
    dupes = int(history.duplicated(subset=["fpl_element_id",
                                           "fpl_fixture_id"]).sum())
    return CheckResult("one row per player per fixture", dupes == 0,
                       f"{dupes} duplicates")


def check_teams_reconcile(matches, players) -> CheckResult:
    """Both sources must resolve to the same canonical club names."""
    match_teams = set(matches[matches["is_current_season"]]["home_team"]) | \
        set(matches[matches["is_current_season"]]["away_team"])
    fpl_teams = set(players["team_name"].dropna())
    only_fpl = fpl_teams - match_teams
    return CheckResult("FPL clubs all appear in match data", not only_fpl,
                       "aligned" if not only_fpl else f"FPL-only: {sorted(only_fpl)}")


REQUIRED = ["match_date", "home_team", "away_team",
            "ft_home_goals", "ft_away_goals", "ft_result"]
NATURAL_KEY = ["season_code", "match_date", "home_team", "away_team"]


def run_all(matches, players, positions, history) -> list[CheckResult]:
    completed = matches[~matches["is_current_season"]]
    live = matches[matches["is_current_season"]]
    return [
        check_no_nulls(matches, REQUIRED),
        check_unique_key(matches, NATURAL_KEY),
        check_result_matches_goals(matches),
        check_no_future_matches(matches),
        check_season_completeness(completed),
        check_each_team_plays_38(completed),
        check_live_within_bounds(live),
        check_live_fixture_spread(live),
        check_prices_plausible(players),
        check_squad_size_is_reachable(players, positions),
        check_minutes_bounded(history),
        check_player_fixture_unique(history),
        check_teams_reconcile(matches, players),
    ]


def main() -> None:
    with stage(log, "quality"):
        i = CONFIG["paths"]["interim"]
        results = run_all(
            pd.read_parquet(i / "matches_clean.parquet"),
            pd.read_parquet(i / "fpl_players.parquet"),
            pd.read_parquet(i / "fpl_positions.parquet"),
            pd.read_parquet(i / "fpl_history.parquet"),
        )
        for r in results:
            level = log.info if r.passed else log.error
            level("[%s] %-46s %s", "PASS" if r.passed else "FAIL", r.name, r.detail)
        failed = [r for r in results if not r.passed]
        if failed:
            raise SystemExit(f"\n{len(failed)} data quality check(s) failed.")
        log.info("all %d checks passed", len(results))


if __name__ == "__main__":
    main()