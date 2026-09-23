-- Q6: The live title race as a running total.
WITH tm AS (
    SELECT tm.*, d.full_date
    FROM team_match tm JOIN dim_date d ON d.date_id = tm.date_id
)
SELECT t.team_name,
       ROW_NUMBER() OVER (PARTITION BY tm.team_id ORDER BY tm.full_date) AS played,
       SUM(tm.points) OVER (PARTITION BY tm.team_id ORDER BY tm.full_date
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
           AS cumulative_points
FROM tm
JOIN dim_team   t ON t.team_id   = tm.team_id
JOIN dim_season s ON s.season_id = tm.season_id
WHERE s.status = 'in_progress'
ORDER BY t.team_name, played;