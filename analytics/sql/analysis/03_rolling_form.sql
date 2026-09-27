-- Q3: Who is in form right now, not who has been good all season?
-- Summed to one row per player per gameweek first, then windowed on the
-- gameweek number itself: a double gameweek counts as one gameweek, and a
-- blank one still uses up a slot in the five.
WITH pf AS (
    SELECT f.player_id, f.gameweek_id,
           SUM(f.total_points) AS total_points,
           SUM(f.minutes)      AS minutes
    FROM fact_player_fixture f
    GROUP BY f.player_id, f.gameweek_id
)
SELECT p.web_name, t.team_name, pos.position_short, p.price_m,
       pf.gameweek_id,
       SUM(pf.total_points) OVER (
           PARTITION BY pf.player_id ORDER BY pf.gameweek_id
           RANGE BETWEEN 4 PRECEDING AND CURRENT ROW
       ) AS points_last_5,
       SUM(pf.minutes) OVER (
           PARTITION BY pf.player_id ORDER BY pf.gameweek_id
           RANGE BETWEEN 4 PRECEDING AND CURRENT ROW
       ) AS minutes_last_5
FROM pf
JOIN dim_player   p   ON p.player_id    = pf.player_id
JOIN dim_team     t   ON t.team_id      = p.team_id
JOIN dim_position pos ON pos.position_id = p.position_id
ORDER BY pf.gameweek_id DESC, points_last_5 DESC;
