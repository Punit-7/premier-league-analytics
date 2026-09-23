# Data dictionary

Every table in `data/processed/epl.duckdb` that the notebooks, app and Power BI read. Staging views (`stg_*`) and landed tables (`raw_*`) are intermediate and not listed.

**Nulls** is the count of null values. **Observed range** is taken from the data as loaded at gameweek 5 (refreshed 23 September 2026), so live-season ranges will widen as the season goes on. The tests that enforce these rules are in `models/**/*.yml`.

## `dim_team`

**Grain:** One row per club that appears in either source.  
**Built by:** dbt `marts/dim_team` · 35 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `team_id` | BIGINT | 0 | 1 to 35 | Surrogate key. |
| `team_name` | VARCHAR | 0 | 35 distinct | Canonical club name (see `src/team_names.py`). |

## `dim_season`

**Grain:** One row per season.  
**Built by:** dbt `marts/dim_season` · 12 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `season_id` | BIGINT | 0 | 1 to 12 | Surrogate key, ordered by season. |
| `season_code` | VARCHAR | 0 | 12 distinct | Source code, e.g. `2627`. |
| `season_label` | VARCHAR | 0 | 12 distinct | Display label, e.g. `2026/27`. |
| `start_year` | INTEGER | 0 | 2015 to 2026 | Calendar year the season starts. |
| `end_year` | INTEGER | 0 | 2016 to 2027 | Calendar year the season ends. |
| `crowd_status` | VARCHAR | 0 | `behind_closed_doors`, `normal`, `partial_behind_closed_doors` | `normal`, or one of the two COVID seasons played partly or fully without crowds. |
| `status` | VARCHAR | 0 | `completed`, `in_progress` | `completed` or `in_progress`. The train/predict boundary for P2. |

## `dim_date`

**Grain:** One row per date on which a match or FPL fixture was played.  
**Built by:** dbt `marts/dim_date` · 1,269 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `date_id` | INTEGER | 0 | 20150808 to 20260920 | Surrogate key as `YYYYMMDD`. |
| `full_date` | DATE | 0 | 2015-08-08 to 2026-09-20 | The date. |
| `year` | BIGINT | 0 | 2015 to 2026 | Calendar year. |
| `month` | BIGINT | 0 | 1 to 12 | Month number. |
| `month_name` | VARCHAR | 0 | 12 distinct | Month name. |
| `day_of_week` | VARCHAR | 0 | `Friday`, `Monday`, `Saturday`, `Sunday`, `Thursday`, `Tuesday`, `Wednesday` | Weekday name. |
| `is_weekend` | BOOLEAN | 0 | true / false | True on Saturday and Sunday. |

## `dim_gameweek`

**Grain:** One row per FPL gameweek in the live season.  
**Built by:** dbt `marts/dim_gameweek` · 38 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `gameweek_id` | INTEGER | 0 | 1 to 38 | FPL gameweek number. |
| `gameweek_name` | VARCHAR | 0 | 38 distinct | FPL display name. |
| `deadline_time` | TIMESTAMP WITH TIME ZONE | 0 | 2026-08-21 23:00:00+05:30 to 2027-05-30 19:00:00+05:30 | Transfer deadline (UTC). |
| `finished` | BOOLEAN | 0 | true / false | True once every fixture in it is complete. |
| `is_current` | BOOLEAN | 0 | true / false | True for the gameweek FPL marks as current. |
| `is_next` | BOOLEAN | 0 | true / false | True for the next gameweek. |
| `average_score` | INTEGER | 0 | 0 to 81 | Mean FPL manager score. 0 until the gameweek is played. |
| `highest_score` | INTEGER | 33 | 119 to 161 | Top FPL manager score. Null until the gameweek is played. |

## `dim_player`

**Grain:** One row per FPL player in the live season. Type 1: current values overwrite.  
**Built by:** dbt `marts/dim_player` · 667 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `player_id` | BIGINT | 0 | 1 to 667 | Surrogate key. |
| `fpl_element_id` | BIGINT | 0 | 1 to 667 | FPL `id`. Stable within a season only. |
| `fpl_player_code` | BIGINT | 0 | 17761 to 700308 | FPL `code`. Stable across seasons; the join key for archives. |
| `web_name` | VARCHAR | 0 | 647 distinct | Short display name. |
| `full_name` | VARCHAR | 0 | 667 distinct | First and last name. |
| `team_id` | BIGINT | 0 | 1 to 31 | Current club, links to `dim_team`. |
| `position_id` | INTEGER | 0 | 1 to 4 | Links to `dim_position`. |
| `price_m` | DOUBLE | 0 | 3.9 to 15.6 | Current price in £m (converted from FPL tenths). |
| `selected_by_percent` | DOUBLE | 0 | 0.0 to 73.7 | Share of FPL managers owning the player. |
| `status` | VARCHAR | 0 | `a`, `d`, `i`, `s`, `u` | FPL availability code: `a` available, `d` doubtful, `i` injured, `s` suspended, `u` unavailable, `n` not in squad. |
| `total_points` | INTEGER | 0 | -1 to 47 | FPL season points as reported by the API. |
| `minutes` | INTEGER | 0 | 0 to 450 | Season minutes as reported by the API. |
| `form` | DOUBLE | 0 | -0.2 to 11.2 | FPL form (average points over recent gameweeks). |
| `points_per_game` | DOUBLE | 0 | -1.0 to 16.0 | FPL points per game. |

## `dim_position`

**Grain:** One row per FPL position.  
**Built by:** dbt `marts/dim_position` · 4 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `position_id` | INTEGER | 0 | 1 to 4 | FPL element type. |
| `position_name` | VARCHAR | 0 | `Defender`, `Forward`, `Goalkeeper`, `Midfielder` | Full name, e.g. `Midfielder`. |
| `position_short` | VARCHAR | 0 | `DEF`, `FWD`, `GKP`, `MID` | `GKP`, `DEF`, `MID` or `FWD`. |
| `squad_select` | INTEGER | 0 | 2 to 5 | Players of this position in a 15-man squad. |
| `squad_min_play` | INTEGER | 0 | 1 to 3 | Minimum in a starting XI. |
| `squad_max_play` | INTEGER | 0 | 1 to 5 | Maximum in a starting XI. |

## `dim_referee`

**Grain:** One row per referee, plus an Unknown member.  
**Built by:** dbt `marts/dim_referee` · 52 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `referee_id` | BIGINT | 0 | 0 to 51 | Surrogate key. `0` is the Unknown member for matches with no referee recorded. |
| `referee_name` | VARCHAR | 0 | 52 distinct | Referee as named in the match CSV. |

## `fact_match`

**Grain:** One row per completed fixture, all seasons.  
**Built by:** dbt `marts/fact_match` · 4,230 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `match_id` | BIGINT | 0 | 1 to 4230 | Surrogate key. |
| `season_id` | BIGINT | 0 | 1 to 12 | Links to `dim_season`. |
| `date_id` | INTEGER | 0 | 20150808 to 20260920 | Links to `dim_date`. |
| `home_team_id` | BIGINT | 0 | 1 to 35 | Links to `dim_team` (role: home). |
| `away_team_id` | BIGINT | 0 | 1 to 35 | Links to `dim_team` (role: away). |
| `referee_id` | BIGINT | 0 | 1 to 51 | Links to `dim_referee`. |
| `kickoff_time` | VARCHAR | 1520 | 25 distinct | Kick-off time as given in the source; absent in early seasons. |
| `ft_home_goals` | INTEGER | 0 | 0 to 9 | Full-time home goals. |
| `ft_away_goals` | INTEGER | 0 | 0 to 9 | Full-time away goals. |
| `ft_result` | VARCHAR | 0 | `A`, `D`, `H` | `H`, `D` or `A`. |
| `ht_home_goals` | INTEGER | 0 | 0 to 5 | Half-time home goals. |
| `ht_away_goals` | INTEGER | 0 | 0 to 5 | Half-time away goals. |
| `ht_result` | VARCHAR | 0 | `A`, `D`, `H` | Half-time `H`, `D` or `A`. |
| `home_shots` | INTEGER | 0 | 0 to 37 | Home shots. |
| `away_shots` | INTEGER | 0 | 0 to 37 | Away shots. |
| `home_shots_on_target` | INTEGER | 0 | 0 to 17 | Home shots on target. |
| `away_shots_on_target` | INTEGER | 0 | 0 to 15 | Away shots on target. |
| `home_fouls` | INTEGER | 0 | 0 to 24 | Home fouls. |
| `away_fouls` | INTEGER | 0 | 1 to 26 | Away fouls. |
| `home_corners` | INTEGER | 0 | 0 to 19 | Home corners. |
| `away_corners` | INTEGER | 0 | 0 to 19 | Away corners. |
| `home_yellows` | INTEGER | 0 | 0 to 7 | Home yellow cards. |
| `away_yellows` | INTEGER | 0 | 0 to 9 | Away yellow cards. |
| `home_reds` | INTEGER | 0 | 0 to 2 | Home red cards. |
| `away_reds` | INTEGER | 0 | 0 to 2 | Away red cards. |
| `home_points` | INTEGER | 0 | 0 to 3 | League points to the home side (3/1/0). |
| `away_points` | INTEGER | 0 | 0 to 3 | League points to the away side. |
| `total_goals` | INTEGER | 0 | 0 to 9 | Home plus away goals. |
| `goal_difference` | INTEGER | 0 | -9 to 9 | Home minus away goals. |

## `fact_player_fixture`

**Grain:** One row per player per fixture. Double gameweeks give two rows.  
**Built by:** dbt `marts/fact_player_fixture` · 3,216 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `player_fixture_id` | INTEGER | 0 | 1 to 3216 | Surrogate key. |
| `player_id` | BIGINT | 0 | 1 to 667 | Links to `dim_player`. |
| `gameweek_id` | INTEGER | 0 | 1 to 5 | Links to `dim_gameweek`. |
| `date_id` | INTEGER | 0 | 20260821 to 20260920 | Links to `dim_date`. |
| `opponent_team_id` | BIGINT | 0 | 1 to 31 | Links to `dim_team` (role: opponent). |
| `fpl_fixture_id` | INTEGER | 0 | 1 to 50 | FPL fixture id. |
| `was_home` | BOOLEAN | 0 | true / false | True if the player's team was at home. |
| `minutes` | INTEGER | 0 | 0 to 90 | Minutes played. |
| `total_points` | INTEGER | 0 | -3 to 23 | FPL points scored in the fixture. |
| `goals_scored` | INTEGER | 0 | 0 to 3 | Goals. |
| `assists` | INTEGER | 0 | 0 to 2 | Assists. |
| `clean_sheets` | INTEGER | 0 | 0 to 1 | 1 if a clean sheet counted for FPL. |
| `goals_conceded` | INTEGER | 0 | 0 to 5 | Goals conceded while on the pitch. |
| `yellow_cards` | INTEGER | 0 | 0 to 1 | Yellow cards. |
| `red_cards` | INTEGER | 0 | 0 to 1 | Red cards. |
| `saves` | INTEGER | 0 | 0 to 8 | Saves. |
| `bonus` | INTEGER | 0 | 0 to 3 | Bonus points (0 to 3). |
| `bps` | INTEGER | 0 | -18 to 92 | Bonus points system raw score. |
| `influence` | DOUBLE | 0 | 0.0 to 132.4 | FPL influence score. |
| `creativity` | DOUBLE | 0 | 0.0 to 98.5 | FPL creativity score. |
| `threat` | DOUBLE | 0 | 0.0 to 84.0 | FPL threat score. |
| `ict_index` | DOUBLE | 0 | 0.0 to 26.1 | FPL ICT index. |
| `price_m` | DOUBLE | 0 | 3.9 to 15.6 | Price in £m at that gameweek. |
| `selected` | INTEGER | 0 | 0 to 7989349 | Number of FPL managers owning the player that gameweek. |
| `transfers_in` | INTEGER | 0 | 0 to 1865890 | Transfers in that gameweek. |
| `transfers_out` | INTEGER | 0 | 0 to 844912 | Transfers out that gameweek. |

## `fact_team_fixture`

**Grain:** One row per team per FPL fixture (two rows per fixture), played and upcoming.  
**Built by:** dbt `marts/fact_team_fixture` · 760 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `team_fixture_id` | BIGINT | 0 | 1 to 760 | Surrogate key. |
| `team_id` | BIGINT | 0 | 1 to 31 | Links to `dim_team`. |
| `opponent_team_id` | BIGINT | 0 | 1 to 31 | Links to `dim_team` (role: opponent). |
| `gameweek_id` | INTEGER | 0 | 1 to 38 | Links to `dim_gameweek`. |
| `fpl_fixture_id` | INTEGER | 0 | 1 to 380 | FPL fixture id. |
| `is_home` | BOOLEAN | 0 | true / false | True if this team is at home. |
| `difficulty` | INTEGER | 0 | 2 to 5 | FPL fixture difficulty for this team, 1 (easy) to 5 (hard). |
| `finished` | BOOLEAN | 0 | true / false | True once played. |

## `team_match`

**Grain:** One row per team per completed match (two per match). Replaces the old `v_team_match` view.  
**Built by:** dbt `analytics/team_match` · 8,460 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `match_id` | BIGINT | 0 | 1 to 4230 | Links to `fact_match`. |
| `season_id` | BIGINT | 0 | 1 to 12 | Links to `dim_season`. |
| `date_id` | INTEGER | 0 | 20150808 to 20260920 | Links to `dim_date`. |
| `team_id` | BIGINT | 0 | 1 to 35 | Links to `dim_team`. |
| `opponent_id` | BIGINT | 0 | 1 to 35 | Links to `dim_team`. |
| `venue` | VARCHAR | 0 | `A`, `H` | `H` or `A`. |
| `goals_for` | INTEGER | 0 | 0 to 9 | Goals scored. |
| `goals_against` | INTEGER | 0 | 0 to 9 | Goals conceded. |
| `points` | INTEGER | 0 | 0 to 3 | League points (3/1/0). |
| `shots` | INTEGER | 0 | 0 to 37 | Shots. |
| `shots_on_target` | INTEGER | 0 | 0 to 17 | Shots on target. |
| `yellows` | INTEGER | 0 | 0 to 9 | Yellow cards. |
| `reds` | INTEGER | 0 | 0 to 2 | Red cards. |

## `player_season`

**Grain:** One row per player: live-season totals with current price. Replaces the old `v_player_season` view.  
**Built by:** dbt `analytics/player_season` · 667 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `player_id` | BIGINT | 0 | 1 to 667 | Links to `dim_player`. |
| `web_name` | VARCHAR | 0 | 647 distinct | Short display name. |
| `full_name` | VARCHAR | 0 | 667 distinct | Full name. |
| `price_m` | DOUBLE | 0 | 3.9 to 15.6 | Current price in £m. |
| `selected_by_percent` | DOUBLE | 0 | 0.0 to 73.7 | Ownership %. |
| `status` | VARCHAR | 0 | `a`, `d`, `i`, `s`, `u` | FPL availability code. |
| `team_name` | VARCHAR | 0 | 20 distinct | Current club. |
| `position_short` | VARCHAR | 0 | `DEF`, `FWD`, `GKP`, `MID` | `GKP`, `DEF`, `MID` or `FWD`. |
| `position_name` | VARCHAR | 0 | `Defender`, `Forward`, `Goalkeeper`, `Midfielder` | Full position name. |
| `fixtures` | BIGINT | 0 | 1 to 5 | Fixtures the player had a row for. |
| `appearances` | HUGEINT | 0 | 0 to 5 | Fixtures with minutes > 0. |
| `minutes` | HUGEINT | 0 | 0 to 450 | Season minutes. |
| `points` | HUGEINT | 0 | -1 to 47 | Season FPL points. |
| `goals` | HUGEINT | 0 | 0 to 5 | Season goals. |
| `assists` | HUGEINT | 0 | 0 to 4 | Season assists. |
| `clean_sheets` | HUGEINT | 0 | 0 to 4 | Season clean sheets. |
| `bonus` | HUGEINT | 0 | 0 to 9 | Season bonus points. |
| `points_per_million` | DOUBLE | 0 | -0.22 to 9.13 | `points / price_m`, rounded to 2 dp. Null if price is 0. |

## `player_value`

**Grain:** One row per player: the points-per-million mart the app and Power BI read.  
**Built by:** dbt `analytics/player_value` · 667 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `player_id` | BIGINT | 0 | 1 to 667 | Links to `dim_player`. |
| `web_name` | VARCHAR | 0 | 647 distinct | Short display name. |
| `position` | VARCHAR | 0 | `DEF`, `FWD`, `GKP`, `MID` | `GKP`, `DEF`, `MID` or `FWD`. |
| `team_name` | VARCHAR | 0 | 20 distinct | Current club. |
| `squad_games` | BIGINT | 0 | 1 to 5 | Fixtures the player had a row for. |
| `full_games` | HUGEINT | 0 | 0 to 5 | Fixtures with 60+ minutes. |
| `unused` | HUGEINT | 0 | 0 to 5 | Fixtures with 0 minutes. |
| `minutes` | HUGEINT | 0 | 0 to 450 | Season minutes. |
| `total_points` | HUGEINT | 0 | -1 to 47 | Season FPL points. |
| `latest_price_m` | DOUBLE | 0 | 4.0 to 15.6 | Highest price seen this season, in £m. |
| `owners` | INTEGER | 0 | 0 to 7989349 | Peak number of FPL managers owning the player. |
| `points_per_million` | DOUBLE | 0 | -0.22 to 9.13 | `total_points / latest_price_m`, 2 dp. |
| `start_rate_pct` | DOUBLE | 0 | 0.0 to 100.0 | `full_games / squad_games` as a %. |

## `refresh_log`

**Grain:** One row per pipeline load; accumulates.  
**Built by:** `src/load.py` · 1 rows

| Column | Type | Nulls | Observed range | Meaning |
|---|---|---|---|---|
| `refreshed_at` | VARCHAR | 0 | `2026-09-23T09:48:37+00:00` | UTC timestamp of the load (ISO 8601 text). |
| `total_matches` | BIGINT | 0 | 4230 to 4230 | Rows in the cleaned match file. |
| `live_matches` | BIGINT | 0 | 50 to 50 | Of which in the live season. |
| `player_fixture_rows` | BIGINT | 0 | 3216 to 3216 | Rows in the FPL player history. |
| `latest_gameweek` | BIGINT | 0 | 5 to 5 | Highest gameweek in the FPL history. |
| `latest_match_date` | VARCHAR | 0 | `2026-09-20` | Most recent live-season match date. |
