-- Q3: Who is in form right now, not who has been good all season?
WITH pf AS (
    SELECT f.player_id, f.gameweek_id, f.total_points, f.minutes
    FROM fact_player_fixture f
)
SELECT p.web_name, t.team_name, pos.position_short, p.price_m,
       pf.gameweek_id,
       SUM(pf.total_points) OVER (
           PARTITION BY pf.player_id ORDER BY pf.gameweek_id
           ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
       ) AS points_last_5,
       SUM(pf.minutes) OVER (
           PARTITION BY pf.player_id ORDER BY pf.gameweek_id
           ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
       ) AS minutes_last_5
FROM pf
JOIN dim_player   p   ON p.player_id    = pf.player_id
JOIN dim_team     t   ON t.team_id      = p.team_id
JOIN dim_position pos ON pos.position_id = p.position_id
ORDER BY pf.gameweek_id DESC, points_last_5 DESC;