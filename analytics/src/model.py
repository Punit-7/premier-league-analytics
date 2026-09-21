"""Build the star schema from the cleaned datasets."""
from datetime import datetime, timezone

import pandas as pd

from src.config import CONFIG

INTERIM = CONFIG["paths"]["interim"]


def read(name: str) -> pd.DataFrame:
    return pd.read_parquet(INTERIM / f"{name}.parquet")

def build_dim_team(matches, players, team_fixtures) -> pd.DataFrame:
    names = sorted(
        set(matches["home_team"]) | set(matches["away_team"])
        | set(players["team_name"].dropna())
        | set(team_fixtures["team_name"].dropna())
    )
    return pd.DataFrame({"team_id": range(1, len(names) + 1), "team_name": names})


def build_dim_season(matches) -> pd.DataFrame:
    s = (matches[["season_code", "season_label"]]
         .drop_duplicates().sort_values("season_code").reset_index(drop=True))
    s.insert(0, "season_id", range(1, len(s) + 1))
    s["start_year"] = ("20" + s["season_code"].str[:2]).astype(int)
    s["end_year"] = ("20" + s["season_code"].str[2:]).astype(int)
    s["crowd_status"] = s["season_code"].map(CONFIG["season_notes"]).fillna("normal")
    s["status"] = s["season_code"].apply(
        lambda c: "in_progress" if c == CONFIG["current_season"] else "completed")
    return s


def build_dim_date(*date_series) -> pd.DataFrame:
    all_dates = pd.concat([pd.Series(s).dropna() for s in date_series])
    d = pd.DataFrame({"full_date": sorted(pd.to_datetime(all_dates).unique())})
    d["full_date"] = pd.to_datetime(d["full_date"])
    d["date_id"] = d["full_date"].dt.strftime("%Y%m%d").astype(int)
    d["year"] = d["full_date"].dt.year
    d["month"] = d["full_date"].dt.month
    d["month_name"] = d["full_date"].dt.strftime("%B")
    d["day_of_week"] = d["full_date"].dt.day_name()
    d["is_weekend"] = (d["full_date"].dt.dayofweek >= 5).astype(int)
    d["full_date"] = d["full_date"].dt.strftime("%Y-%m-%d")
    return d[["date_id", "full_date", "year", "month", "month_name",
              "day_of_week", "is_weekend"]]


def build_dim_referee(matches) -> pd.DataFrame:
    names = sorted(n for n in matches["referee"].dropna().unique() if str(n).strip())
    return pd.concat([
        pd.DataFrame({"referee_id": [0], "referee_name": ["Unknown"]}),
        pd.DataFrame({"referee_id": range(1, len(names) + 1), "referee_name": names}),
    ], ignore_index=True)


def build_dim_player(players, teams) -> pd.DataFrame:
    key = dict(zip(teams["team_name"], teams["team_id"]))
    p = players.copy()
    p["team_id"] = p["team_name"].map(key)
    p = p.sort_values("fpl_element_id").reset_index(drop=True)
    p.insert(0, "player_id", range(1, len(p) + 1))
    p["full_name"] = p["first_name"] + " " + p["second_name"]
    return p[["player_id", "fpl_element_id", "fpl_player_code", "web_name",
              "full_name", "team_id", "position_id", "price_m",
              "selected_by_percent", "status", "total_points", "minutes",
              "form", "points_per_game"]]


def build_fact_match(matches, teams, seasons, refs) -> pd.DataFrame:
    tk = dict(zip(teams["team_name"], teams["team_id"]))
    sk = dict(zip(seasons["season_code"], seasons["season_id"]))
    rk = dict(zip(refs["referee_name"], refs["referee_id"]))

    f = matches.copy()
    f["home_team_id"] = f["home_team"].map(tk)
    f["away_team_id"] = f["away_team"].map(tk)
    f["season_id"] = f["season_code"].map(sk)
    f["date_id"] = f["match_date"].dt.strftime("%Y%m%d").astype(int)
    f["referee_id"] = f["referee"].map(rk).fillna(0).astype(int)

    cols = ["match_id", "season_id", "date_id", "home_team_id", "away_team_id",
            "referee_id", "kickoff_time", "ft_home_goals", "ft_away_goals",
            "ft_result", "ht_home_goals", "ht_away_goals", "ht_result",
            "home_shots", "away_shots", "home_shots_on_target",
            "away_shots_on_target", "home_fouls", "away_fouls", "home_corners",
            "away_corners", "home_yellows", "away_yellows", "home_reds",
            "away_reds", "home_points", "away_points", "total_goals",
            "goal_difference"]
    return f[[c for c in cols if c in f.columns]]


def build_fact_player_fixture(history, players_dim, teams, dates) -> pd.DataFrame:
    pk = dict(zip(players_dim["fpl_element_id"], players_dim["player_id"]))
    tk = dict(zip(teams["team_name"], teams["team_id"]))
    valid_dates = set(dates["date_id"])

    f = history.copy()
    f["player_id"] = f["fpl_element_id"].map(pk)
    f["opponent_team_id"] = f["opponent_name"].map(tk)
    f["date_id"] = f["match_date"].dt.strftime("%Y%m%d").astype("Int64")
    f.loc[~f["date_id"].isin(valid_dates), "date_id"] = pd.NA

    f = f[f["player_id"].notna()].copy()
    f["player_id"] = f["player_id"].astype(int)
    f["was_home"] = f["was_home"].astype(int)

    cols = ["player_fixture_id", "player_id", "gameweek_id", "date_id",
            "opponent_team_id", "fpl_fixture_id", "was_home", "minutes",
            "total_points", "goals_scored", "assists", "clean_sheets",
            "goals_conceded", "yellow_cards", "red_cards", "saves", "bonus",
            "bps", "influence", "creativity", "threat", "ict_index",
            "price_m", "selected", "transfers_in", "transfers_out"]
    return f[cols]


def build_fact_team_fixture(team_fixtures, teams) -> pd.DataFrame:
    tk = dict(zip(teams["team_name"], teams["team_id"]))
    f = team_fixtures.copy()
    f["team_id"] = f["team_name"].map(tk)
    f["opponent_team_id"] = f["opponent_name"].map(tk)
    f["is_home"] = f["is_home"].astype(int)
    f["finished"] = f["finished"].astype(int)
    f = f.reset_index(drop=True)
    f.insert(0, "team_fixture_id", range(1, len(f) + 1))
    return f[["team_fixture_id", "team_id", "opponent_team_id", "gameweek_id",
              "fpl_fixture_id", "is_home", "difficulty", "finished"]]


def build_refresh_row(matches, history) -> pd.DataFrame:
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


def build_all() -> dict[str, pd.DataFrame]:
    matches = read("matches_clean")
    players = read("fpl_players")
    positions = read("fpl_positions")
    gameweeks = read("fpl_gameweeks")
    team_fixtures = read("fpl_team_fixtures")
    history = read("fpl_history")

    teams = build_dim_team(matches, players, team_fixtures)
    seasons = build_dim_season(matches)
    dates = build_dim_date(matches["match_date"], history["match_date"])
    refs = build_dim_referee(matches)
    dim_player = build_dim_player(players, teams)

    tables = {
        "dim_team": teams,
        "dim_season": seasons,
        "dim_date": dates,
        "dim_referee": refs,
        "dim_position": positions,
        "dim_gameweek": gameweeks,
        "dim_player": dim_player,
        "fact_match": build_fact_match(matches, teams, seasons, refs),
        "fact_player_fixture": build_fact_player_fixture(
            history, dim_player, teams, dates),
        "fact_team_fixture": build_fact_team_fixture(team_fixtures, teams),
        "refresh_log": build_refresh_row(matches, history),
    }

    assert tables["fact_match"]["match_id"].is_unique
    assert tables["fact_player_fixture"]["player_fixture_id"].is_unique
    assert tables["fact_match"]["home_team_id"].notna().all()
    assert tables["dim_player"]["team_id"].notna().all(), "unmapped player team"
    return tables