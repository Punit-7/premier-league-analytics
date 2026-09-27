import pandas as pd

from src.quality import (check_minutes_bounded, check_player_fixture_unique,
                         check_prices_plausible)


def test_price_bounds_catch_a_bad_conversion():
    """A forgotten divide-by-10 shows up as a GBP 55m player."""
    assert not check_prices_plausible(pd.DataFrame({"price_m": [5.5, 55.0]})).passed
    assert check_prices_plausible(pd.DataFrame({"price_m": [5.5, 12.0]})).passed


def test_double_gameweek_is_not_a_duplicate():
    """Same player, same gameweek, two fixtures — legal."""
    df = pd.DataFrame({"fpl_element_id": [1, 1], "fpl_fixture_id": [10, 11]})
    assert check_player_fixture_unique(df).passed


def test_same_fixture_twice_is_a_duplicate():
    df = pd.DataFrame({"fpl_element_id": [1, 1], "fpl_fixture_id": [10, 10]})
    assert not check_player_fixture_unique(df).passed


def test_minutes_bounds():
    assert check_minutes_bounded(pd.DataFrame({"minutes": [0, 90, 120]})).passed
    assert not check_minutes_bounded(pd.DataFrame({"minutes": [95, 200]})).passed