-- Q1: Current standings, ranked the way the league ranks them.

SELECT RANK() OVER (ORDER BY SUM(tm.points) DESC,
                    SUM(tm.goals_for) - SUM(tm.goals_against) DESC,
                    SUM(tm.goals_for) DESC)        AS position,
       t.team_name, COUNT(*) AS played,
       SUM(CASE WHEN tm.points=3 THEN 1 ELSE 0 END) AS won,
       SUM(CASE WHEN tm.points=1 THEN 1 ELSE 0 END) AS drawn,
       SUM(CASE WHEN tm.points=0 THEN 1 ELSE 0 END) AS lost,
       SUM(tm.goals_for) AS gf, SUM(tm.goals_against) AS ga,
       SUM(tm.goals_for) - SUM(tm.goals_against) AS gd,
       SUM(tm.points) AS points
FROM team_match tm
JOIN dim_team   t ON t.team_id   = tm.team_id
JOIN dim_season s ON s.season_id = tm.season_id
WHERE s.status = 'in_progress'
GROUP BY t.team_name
ORDER BY position;