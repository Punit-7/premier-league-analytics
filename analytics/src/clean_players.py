"""FPL JSON to tidy player tables. Deterministic and re-runnable."""
import json

import pandas as pd

from src.config import CONFIG
from src.profile import read_fpl
from src.team_names import canonical, by_fpl_id
from src.logging_setup import get_logger, stage

log = get_logger(__name__)

def clean_players() -> dict[str, pd.DataFrame]:
    boot = read_fpl("bootstrap")
    fixtures = read_fpl("fixtures")
    
    fpl_teams = pd.DataFrame(boot["teams"])[["id", "name", "short_name"]]
    fpl_teams["team_name"] = fpl_teams["name"].map(lambda n: canonical(n, "fpl"))
    team_by_fpl_id = dict(zip(fpl_teams["id"], fpl_teams["team_name"]))

    positions = pd.DataFrame(boot["element_types"])[
        ["id", "singular_name", "singular_name_short",
         "squad_select", "squad_min_play", "squad_max_play"]
    ].rename(columns={"id": "position_id", "singular_name": "position_name",
                      "singular_name_short": "position_short"})

    gameweeks = pd.DataFrame(boot["events"])[
        ["id", "name", "deadline_time", "finished", "is_current", "is_next",
         "average_entry_score", "highest_score"]
    ].rename(columns={"id": "gameweek_id", "name": "gameweek_name",
                      "average_entry_score": "average_score"})
    gameweeks["deadline_time"] = pd.to_datetime(gameweeks["deadline_time"],
                                                utc=True, errors="coerce")
    
    players = pd.DataFrame(boot["elements"])[
        ["id", "code", "first_name", "second_name", "web_name", "team",
         "element_type", "now_cost", "selected_by_percent", "status",
         "total_points", "minutes", "form", "points_per_game"]
    ].rename(columns={"id": "fpl_element_id", "code": "fpl_player_code",
                      "team": "fpl_team_id", "element_type": "position_id"})
    
    players["team_name"] = players["fpl_team_id"].map(
        lambda i: by_fpl_id(team_by_fpl_id, i))
    players["price_m"] = players["now_cost"] / 10.0          # tenths -> millions
    
    for col in ("selected_by_percent", "form", "points_per_game"):
        players[col] = pd.to_numeric(players[col], errors="coerce")
    
    players = players.drop(columns=["now_cost", "fpl_team_id"])
    
    # Upcoming fixtures with FPL's own difficulty ratings, one row per team
    upcoming = []
    for f in fixtures:
        if f.get("event") is None:
            continue
        upcoming.append({"gameweek_id": f["event"], "fpl_fixture_id": f["id"],
                         "team_name": by_fpl_id(team_by_fpl_id, f["team_h"]),
                         "opponent_name": by_fpl_id(team_by_fpl_id, f["team_a"]),
                         "is_home": True, "difficulty": f["team_h_difficulty"],
                         "finished": bool(f.get("finished"))})
        upcoming.append({"gameweek_id": f["event"], "fpl_fixture_id": f["id"],
                         "team_name": by_fpl_id(team_by_fpl_id, f["team_a"]),
                         "opponent_name": by_fpl_id(team_by_fpl_id, f["team_h"]),
                         "is_home": False, "difficulty": f["team_a_difficulty"],
                         "finished": bool(f.get("finished"))})
    team_fixtures = pd.DataFrame(upcoming)

    # Per-player, per-fixture history. Grain is player x fixture, NOT
    # player x gameweek — double gameweeks exist.
    rows = []
    raw_dir = CONFIG["paths"]["fpl_raw"]
    for element_id in players["fpl_element_id"]:
        path = raw_dir / f"player_{element_id}.json"
        if not path.exists():
            continue
        for h in json.loads(path.read_text()).get("history", []):
            rows.append({
                "fpl_element_id": element_id,
                "gameweek_id": h["round"],
                "fpl_fixture_id": h["fixture"],
                "opponent_name": by_fpl_id(team_by_fpl_id, h["opponent_team"]),
                "kickoff_time": h["kickoff_time"],
                "was_home": h["was_home"],
                "minutes": h["minutes"], "total_points": h["total_points"],
                "goals_scored": h["goals_scored"], "assists": h["assists"],
                "clean_sheets": h["clean_sheets"],
                "goals_conceded": h["goals_conceded"],
                "yellow_cards": h["yellow_cards"], "red_cards": h["red_cards"],
                "saves": h["saves"], "bonus": h["bonus"], "bps": h["bps"],
                "influence": float(h["influence"]),
                "creativity": float(h["creativity"]),
                "threat": float(h["threat"]),
                "ict_index": float(h["ict_index"]),
                "price_m": h["value"] / 10.0,
                "selected": h["selected"],
                "transfers_in": h["transfers_in"],
                "transfers_out": h["transfers_out"],
            })
            
    history = pd.DataFrame(rows, columns=[
        "fpl_element_id", "gameweek_id", "fpl_fixture_id", "opponent_name",
        "kickoff_time", "was_home", "minutes", "total_points", "goals_scored",
        "assists", "clean_sheets", "goals_conceded", "yellow_cards",
        "red_cards", "saves", "bonus", "bps", "influence", "creativity",
        "threat", "ict_index", "price_m", "selected", "transfers_in",
        "transfers_out",
    ])
    history["kickoff_time"] = pd.to_datetime(history["kickoff_time"],
                                             utc=True, errors="coerce")
    history["match_date"] = history["kickoff_time"].dt.tz_convert(None).dt.normalize()
    history = history.drop_duplicates(subset=["fpl_element_id", "fpl_fixture_id"])
    history = history.sort_values(["gameweek_id", "fpl_element_id"]).reset_index(drop=True)
    history.insert(0, "player_fixture_id", range(1, len(history) + 1))

    return {"players": players, "positions": positions,
            "gameweeks": gameweeks, "team_fixtures": team_fixtures,
            "history": history}
    
def main() -> None:
    with stage(log, "clean_players"):
        fpl = clean_players()
        log.info("FPL: %d players, %d player-fixture rows, %d team-fixture rows",
                 len(fpl["players"]), len(fpl["history"]),
                 len(fpl["team_fixtures"]))

        interim = CONFIG["paths"]["interim"]
        for name, df in fpl.items():
            df.to_parquet(interim / f"fpl_{name}.parquet", index=False)
        log.info("wrote cleaned FPL data to %s", interim)

if __name__ == "__main__":
    main()
