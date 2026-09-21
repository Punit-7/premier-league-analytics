"""Canonical club names. Two sources, two conventions, one dimension."""

MATCH_ALIASES = {
    "Arsenal": "Arsenal", "Aston Villa": "Aston Villa",
    "Bournemouth": "AFC Bournemouth", "Brentford": "Brentford",
    "Brighton": "Brighton & Hove Albion", "Burnley": "Burnley",
    "Cardiff": "Cardiff City", "Chelsea": "Chelsea",
    "Coventry": "Coventry City", "Crystal Palace": "Crystal Palace",
    "Everton": "Everton", "Fulham": "Fulham",
    "Huddersfield": "Huddersfield Town", "Hull": "Hull City",
    "Ipswich": "Ipswich Town", "Leeds": "Leeds United",
    "Leicester": "Leicester City", "Liverpool": "Liverpool",
    "Luton": "Luton Town", "Man City": "Manchester City",
    "Man United": "Manchester United", "Middlesbrough": "Middlesbrough",
    "Newcastle": "Newcastle United", "Norwich": "Norwich City",
    "Nott'm Forest": "Nottingham Forest",
    "Sheffield United": "Sheffield United", "Sheffield Utd": "Sheffield United",
    "Southampton": "Southampton", "Stoke": "Stoke City",
    "Sunderland": "Sunderland", "Swansea": "Swansea City",
    "Tottenham": "Tottenham Hotspur", "Watford": "Watford",
    "West Brom": "West Bromwich Albion", "West Ham": "West Ham United",
    "Wolves": "Wolverhampton Wanderers",
}

# FPL's `name` field. Differs from football-data on several clubs.
FPL_ALIASES = {
    "Arsenal": "Arsenal", "Aston Villa": "Aston Villa",
    "Bournemouth": "AFC Bournemouth", "Brentford": "Brentford",
    "Brighton": "Brighton & Hove Albion", "Burnley": "Burnley",
    "Chelsea": "Chelsea", "Coventry": "Coventry City",
    "Coventry City": "Coventry City",
    "Crystal Palace": "Crystal Palace", "Everton": "Everton",
    "Fulham": "Fulham", "Hull": "Hull City", "Hull City": "Hull City",
    "Ipswich": "Ipswich Town", "Ipswich Town": "Ipswich Town",
    "Leeds": "Leeds United", "Leicester": "Leicester City",
    "Liverpool": "Liverpool", "Man City": "Manchester City",
    "Man Utd": "Manchester United", "Newcastle": "Newcastle United",
    "Nott'm Forest": "Nottingham Forest", "Southampton": "Southampton",
    "Spurs": "Tottenham Hotspur", "Sunderland": "Sunderland",
    "West Ham": "West Ham United", "Wolves": "Wolverhampton Wanderers",
}


def canonical(name: str, source: str = "match") -> str:
    table = MATCH_ALIASES if source == "match" else FPL_ALIASES
    key = str(name).strip()
    if key not in table:
        raise KeyError(
            f"Unmapped {source} team name: {key!r}. Add it to "
            f"src/team_names.py — do not guess at runtime."
        )
    return table[key]


def by_fpl_id(team_by_fpl_id: dict[int, str], team_id: int) -> str:
    """Look up a canonical team name by FPL numeric team id. Raises rather
    than returning NaN/None on a miss, so an id one source doesn't recognise
    fails loudly instead of silently dropping a club downstream."""
    if team_id not in team_by_fpl_id:
        raise KeyError(
            f"FPL team id {team_id!r} is not in the bootstrap teams list. "
            f"Sources disagree — re-run src/ingest_fpl.py, do not guess."
        )
    return team_by_fpl_id[team_id]