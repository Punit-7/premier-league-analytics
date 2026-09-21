PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS v_team_match;
DROP VIEW  IF EXISTS v_player_season;
DROP TABLE IF EXISTS fact_player_fixture;
DROP TABLE IF EXISTS fact_team_fixture;
DROP TABLE IF EXISTS fact_match;
DROP TABLE IF EXISTS dim_player;
DROP TABLE IF EXISTS dim_position;
DROP TABLE IF EXISTS dim_gameweek;
DROP TABLE IF EXISTS dim_team;
DROP TABLE IF EXISTS dim_season;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_referee;

CREATE TABLE IF NOT EXISTS refresh_log (
    refreshed_at        TEXT PRIMARY KEY,
    total_matches       INTEGER NOT NULL,
    live_matches        INTEGER NOT NULL,
    player_fixture_rows INTEGER NOT NULL,
    latest_gameweek     INTEGER,
    latest_match_date   TEXT
);

CREATE TABLE dim_team (
    team_id   INTEGER PRIMARY KEY,
    team_name TEXT    NOT NULL UNIQUE
);

CREATE TABLE dim_season (
    season_id    INTEGER PRIMARY KEY,
    season_code  TEXT    NOT NULL UNIQUE,
    season_label TEXT    NOT NULL,
    start_year   INTEGER NOT NULL,
    end_year     INTEGER NOT NULL,
    crowd_status TEXT    NOT NULL,
    status       TEXT    NOT NULL CHECK (status IN ('completed','in_progress'))
);

CREATE TABLE dim_date (
    date_id     INTEGER PRIMARY KEY,
    full_date   TEXT    NOT NULL,
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    month_name  TEXT    NOT NULL,
    day_of_week TEXT    NOT NULL,
    is_weekend  INTEGER NOT NULL
);

CREATE TABLE dim_referee (
    referee_id   INTEGER PRIMARY KEY,
    referee_name TEXT    NOT NULL UNIQUE
);

CREATE TABLE dim_position (
    position_id    INTEGER PRIMARY KEY,
    position_name  TEXT    NOT NULL UNIQUE,
    position_short TEXT    NOT NULL,
    squad_select   INTEGER NOT NULL,
    squad_min_play INTEGER NOT NULL,
    squad_max_play INTEGER NOT NULL
);

CREATE TABLE dim_gameweek (
    gameweek_id    INTEGER PRIMARY KEY,
    gameweek_name  TEXT    NOT NULL,
    deadline_time  TEXT,
    finished       INTEGER NOT NULL,
    is_current     INTEGER NOT NULL,
    is_next        INTEGER NOT NULL,
    average_score  INTEGER,
    highest_score  INTEGER
);

CREATE TABLE dim_player (
    player_id           INTEGER PRIMARY KEY,
    fpl_element_id      INTEGER NOT NULL UNIQUE,
    fpl_player_code     INTEGER NOT NULL,
    web_name            TEXT    NOT NULL,
    full_name           TEXT    NOT NULL,
    team_id             INTEGER NOT NULL REFERENCES dim_team(team_id),
    position_id         INTEGER NOT NULL REFERENCES dim_position(position_id),
    price_m             REAL    NOT NULL CHECK (price_m > 0),
    selected_by_percent REAL,
    status              TEXT,
    total_points        INTEGER,
    minutes             INTEGER,
    form                REAL,
    points_per_game     REAL
);

CREATE TABLE fact_match (
    match_id             INTEGER PRIMARY KEY,
    season_id            INTEGER NOT NULL REFERENCES dim_season(season_id),
    date_id              INTEGER NOT NULL REFERENCES dim_date(date_id),
    home_team_id         INTEGER NOT NULL REFERENCES dim_team(team_id),
    away_team_id         INTEGER NOT NULL REFERENCES dim_team(team_id),
    referee_id           INTEGER NOT NULL REFERENCES dim_referee(referee_id),
    kickoff_time         TEXT,
    ft_home_goals        INTEGER NOT NULL CHECK (ft_home_goals >= 0),
    ft_away_goals        INTEGER NOT NULL CHECK (ft_away_goals >= 0),
    ft_result            TEXT    NOT NULL CHECK (ft_result IN ('H','D','A')),
    ht_home_goals        INTEGER, ht_away_goals INTEGER, ht_result TEXT,
    home_shots           INTEGER, away_shots INTEGER,
    home_shots_on_target INTEGER, away_shots_on_target INTEGER,
    home_fouls           INTEGER, away_fouls INTEGER,
    home_corners         INTEGER, away_corners INTEGER,
    home_yellows         INTEGER, away_yellows INTEGER,
    home_reds            INTEGER, away_reds INTEGER,
    home_points          INTEGER NOT NULL,
    away_points          INTEGER NOT NULL,
    total_goals          INTEGER NOT NULL,
    goal_difference      INTEGER NOT NULL,
    CHECK (home_team_id != away_team_id),
    UNIQUE (season_id, date_id, home_team_id, away_team_id)
);

CREATE TABLE fact_player_fixture (
    player_fixture_id INTEGER PRIMARY KEY,
    player_id         INTEGER NOT NULL REFERENCES dim_player(player_id),
    gameweek_id       INTEGER NOT NULL REFERENCES dim_gameweek(gameweek_id),
    date_id           INTEGER          REFERENCES dim_date(date_id),
    opponent_team_id  INTEGER          REFERENCES dim_team(team_id),
    fpl_fixture_id    INTEGER NOT NULL,
    was_home          INTEGER NOT NULL CHECK (was_home IN (0,1)),
    minutes           INTEGER NOT NULL CHECK (minutes BETWEEN 0 AND 120),
    total_points      INTEGER NOT NULL,
    goals_scored      INTEGER NOT NULL CHECK (goals_scored >= 0),
    assists           INTEGER NOT NULL CHECK (assists >= 0),
    clean_sheets      INTEGER NOT NULL,
    goals_conceded    INTEGER NOT NULL,
    yellow_cards      INTEGER NOT NULL,
    red_cards         INTEGER NOT NULL,
    saves             INTEGER NOT NULL,
    bonus             INTEGER NOT NULL CHECK (bonus BETWEEN 0 AND 3),
    bps               INTEGER NOT NULL,
    influence         REAL, creativity REAL, threat REAL, ict_index REAL,
    price_m           REAL    NOT NULL CHECK (price_m > 0),
    selected          INTEGER, transfers_in INTEGER, transfers_out INTEGER,
    UNIQUE (player_id, fpl_fixture_id)
);

CREATE TABLE fact_team_fixture (
    team_fixture_id  INTEGER PRIMARY KEY,
    team_id          INTEGER NOT NULL REFERENCES dim_team(team_id),
    opponent_team_id INTEGER NOT NULL REFERENCES dim_team(team_id),
    gameweek_id      INTEGER NOT NULL REFERENCES dim_gameweek(gameweek_id),
    fpl_fixture_id   INTEGER NOT NULL,
    is_home          INTEGER NOT NULL CHECK (is_home IN (0,1)),
    difficulty       INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
    finished         INTEGER NOT NULL,
    UNIQUE (team_id, fpl_fixture_id)
);

CREATE INDEX idx_fact_season   ON fact_match(season_id);
CREATE INDEX idx_fact_date     ON fact_match(date_id);
CREATE INDEX idx_fact_home     ON fact_match(home_team_id);
CREATE INDEX idx_fact_away     ON fact_match(away_team_id);
CREATE INDEX idx_pf_player     ON fact_player_fixture(player_id);
CREATE INDEX idx_pf_gameweek   ON fact_player_fixture(gameweek_id);
CREATE INDEX idx_tf_team_gw    ON fact_team_fixture(team_id, gameweek_id);

-- One row per team per match. Team-level analysis builds on this.
CREATE VIEW v_team_match AS
SELECT match_id, season_id, date_id,
       home_team_id AS team_id, away_team_id AS opponent_id, 'H' AS venue,
       ft_home_goals AS goals_for, ft_away_goals AS goals_against,
       home_points AS points, home_shots AS shots,
       home_shots_on_target AS shots_on_target,
       home_yellows AS yellows, home_reds AS reds
FROM fact_match
UNION ALL
SELECT match_id, season_id, date_id,
       away_team_id, home_team_id, 'A',
       ft_away_goals, ft_home_goals, away_points,
       away_shots, away_shots_on_target, away_yellows, away_reds
FROM fact_match;

-- One row per player: season totals with their current price attached.
CREATE VIEW v_player_season AS
SELECT p.player_id, p.web_name, p.full_name, p.price_m,
       p.selected_by_percent, p.status,
       t.team_name, pos.position_short, pos.position_name,
       COUNT(f.player_fixture_id)                  AS fixtures,
       SUM(CASE WHEN f.minutes > 0 THEN 1 ELSE 0 END) AS appearances,
       SUM(f.minutes)                              AS minutes,
       SUM(f.total_points)                         AS points,
       SUM(f.goals_scored)                         AS goals,
       SUM(f.assists)                              AS assists,
       SUM(f.clean_sheets)                         AS clean_sheets,
       SUM(f.bonus)                                AS bonus,
       ROUND(SUM(f.total_points) / p.price_m, 2)   AS points_per_million
FROM dim_player p
JOIN dim_team     t   ON t.team_id       = p.team_id
JOIN dim_position pos ON pos.position_id = p.position_id
LEFT JOIN fact_player_fixture f ON f.player_id = p.player_id
GROUP BY p.player_id;