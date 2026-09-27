-- Q10: Bonus points are invisible in a scoreline but decide FPL weeks.
SELECT p.web_name, t.team_name, pos.position_short, p.price_m,
       SUM(f.bonus)                                        AS bonus_points,
       SUM(f.total_points)                                 AS total_points,
       ROUND(100.0*SUM(f.bonus)/NULLIF(SUM(f.total_points),0), 1)
                                                           AS pct_from_bonus,
       ROUND(AVG(f.bps), 1)                                AS avg_bps
FROM fact_player_fixture f
JOIN dim_player   p   ON p.player_id     = f.player_id
JOIN dim_team     t   ON t.team_id       = p.team_id
JOIN dim_position pos ON pos.position_id = p.position_id
WHERE f.minutes > 0
GROUP BY p.player_id, p.web_name, t.team_name, pos.position_short, p.price_m
HAVING SUM(f.minutes) >= 270
ORDER BY bonus_points DESC LIMIT 25;