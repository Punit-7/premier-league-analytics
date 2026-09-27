import pandas as pd
import pytest

from src.clean_matches import clean_matches
from src.team_names import canonical


def make_row(**overrides) -> dict:
    row = {
        "match_date": "12/08/2026", "kickoff_time": "15:00",
        "home_team": "Arsenal", "away_team": "Coventry",
        "ft_home_goals": 2, "ft_away_goals": 1, "ft_result": "H",
        "ht_home_goals": 1, "ht_away_goals": 0, "ht_result": "H",
        "referee": "M Oliver",
        "home_shots": 12, "away_shots": 9,
        "home_shots_on_target": 5, "away_shots_on_target": 3,
        "home_fouls": 10, "away_fouls": 11,
        "home_corners": 6, "away_corners": 4,
        "home_yellows": 1, "away_yellows": 2, "home_reds": 0, "away_reds": 0,
        "season_code": "2627", "season_label": "2026/27", "is_current_season": True,
    }
    row.update(overrides)
    return row


def test_both_sources_map_to_the_same_canonical_name():
    assert canonical("Man United", "match") == canonical("Man Utd", "fpl")
    assert canonical("Tottenham", "match") == canonical("Spurs", "fpl")


def test_unknown_team_raises():
    with pytest.raises(KeyError):
        canonical("Real Madrid", "match")


def test_points_derived_from_result():
    df, _ = clean_matches(pd.DataFrame([make_row()]))
    assert df.loc[0, "home_points"] == 3 and df.loc[0, "away_points"] == 0


def test_dates_parsed_day_first():
    df, _ = clean_matches(pd.DataFrame([make_row(match_date="12/08/2026")]))
    assert (df.loc[0, "match_date"].day, df.loc[0, "match_date"].month) == (12, 8)


def test_unplayed_fixture_rejected():
    df, rejects = clean_matches(pd.DataFrame([make_row(ft_result=None)]))
    assert df.empty
    assert "fixture not yet played" in set(rejects["reject_reason"])


def test_duplicate_rejected():
    df, rejects = clean_matches(pd.DataFrame([make_row(), make_row()]))
    assert len(df) == 1