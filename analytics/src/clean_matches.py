"""Raw match CSVs to one validated dataset. Deterministic and re-runnable."""

import pandas as pd

from src.config import CONFIG
from src.profile import read_raw_match
from src.team_names import canonical
from src.logging_setup import get_logger, stage

log = get_logger(__name__)

RENAME = {
    "Date": "match_date", "Time": "kickoff_time",
    "HomeTeam": "home_team", "AwayTeam": "away_team",
    "FTHG": "ft_home_goals", "FTAG": "ft_away_goals", "FTR": "ft_result",
    "HTHG": "ht_home_goals", "HTAG": "ht_away_goals", "HTR": "ht_result",
    "Referee": "referee", "HS": "home_shots", "AS": "away_shots",
    "HST": "home_shots_on_target", "AST": "away_shots_on_target",
    "HF": "home_fouls", "AF": "away_fouls",
    "HC": "home_corners", "AC": "away_corners",
    "HY": "home_yellows", "AY": "away_yellows",
    "HR": "home_reds", "AR": "away_reds"
}

COUNTS = ["ft_home_goals", "ft_away_goals", "ht_home_goals", "ht_away_goals",
          "home_shots", "away_shots", "home_shots_on_target",
          "away_shots_on_target", "home_fouls", "away_fouls",
          "home_corners", "away_corners", "home_yellows", "away_yellows",
          "home_reds", "away_reds"]

def load_matches() -> pd.DataFrame:
    frames = []
    for season in CONFIG["all_seasons"]:
        df = read_raw_match(season)
        df = df[[c for c in RENAME if c in df.columns]].rename(columns=RENAME)
        df["season_code"] = season
        df["season_label"] = f"20{season[:2]}/{season[2:]}"
        df["is_current_season"] = season == CONFIG["current_season"]
        frames.append(df)
    return pd.concat(frames, ignore_index=True)

def clean_matches(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rejects = []
    
    def reject(mask, reason):
        if mask.any():
            bad = df.loc[mask].copy()
            bad["reject_reason"] = reason
            rejects.append(bad)
    
    empty = df["match_date"].isna() & df["home_team"].isna()
    reject(empty, "empty row")
    df = df.loc[~empty].copy()
    
    unplayed = df["ft_result"].isna() | \
        (df["ft_result"].astype("string").str.strip() == "")
    reject(unplayed, "fixture not yet played")
    df = df.loc[~unplayed].copy()
    
    df["match_date"] = pd.to_datetime(df["match_date"], dayfirst=True, format= "mixed", errors="coerce")
    
    bad_date = df["match_date"].isna()
    reject(bad_date,"unparseable data")
    df = df.loc[~bad_date].copy()
    
    df["home_team"] = df["home_team"].map(lambda n: canonical(n, "match"))
    df["away_team"] = df["away_team"].map(lambda n: canonical(n, "match"))
    
    for col in COUNTS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    
    for col in ("ft_result","ht_result"):
        df[col] = df[col].astype("string").str.strip().str.upper()
    
    df["referee"] = df["referee"].astype("string").str.strip()
    
    limit = CONFIG["expectations"]["max_plausible_goals"]
    bad_goals = ((df["ft_home_goals"] > limit) | (df["ft_away_goals"] > limit)
                 | (df["ft_home_goals"] < 0) | (df["ft_away_goals"] < 0)).fillna(True)
    reject(bad_goals, "goals outside plausible range")
    df = df.loc[~bad_goals].copy()
    
    half_over = ((df["ht_home_goals"] > df["ft_home_goals"])
                 | (df["ht_away_goals"] > df["ft_away_goals"])).fillna(False)
    reject(half_over, "half-time goals exceed full-time")
    df = df.loc[~half_over].copy()

    bad_result = ~df["ft_result"].isin(["H", "D", "A"])
    reject(bad_result, "result not in H/D/A")
    df = df.loc[~bad_result].copy()

    key = ["season_code", "match_date", "home_team", "away_team"]
    dupes = df.duplicated(subset=key, keep="first")
    reject(dupes, "duplicate on natural key")
    df = df.loc[~dupes].copy()
    
    df["total_goals"] = df["ft_home_goals"] + df["ft_away_goals"]
    df["goal_difference"] = df["ft_home_goals"] - df["ft_away_goals"]
    df["home_points"] = df["ft_result"].map({"H": 3, "D": 1, "A": 0}).astype("Int64")
    df["away_points"] = df["ft_result"].map({"A": 3, "D": 1, "H": 0}).astype("Int64")

    df = df.sort_values(["match_date", "home_team"]).reset_index(drop=True)
    df.insert(0, "match_id", range(1, len(df) + 1))
    return df, (pd.concat(rejects, ignore_index=True) if rejects else pd.DataFrame())

def main() -> None:
    with stage(log, "clean_matches"):
        matches, rejects = clean_matches(load_matches())
        live = matches[matches["is_current_season"]]
        log.info("matches: kept %d (%d historical, %d live), rejected %d",
                 len(matches), len(matches) - len(live), len(live), len(rejects))
        if not rejects.empty:
            for reason, count in rejects["reject_reason"].value_counts().items():
                log.warning("rejected %d rows: %s", count, reason)

        interim = CONFIG["paths"]["interim"]
        matches.to_parquet(interim / "matches_clean.parquet", index=False)
        if not rejects.empty:
            rejects.to_csv(interim / "rejects.csv", index=False)
        log.info("wrote cleaned matches to %s", interim)


if __name__ == "__main__":
    main()
