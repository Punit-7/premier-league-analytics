-- Q4: Whose fixtures get easier soon? The core FPL planning question.
WITH next_gw AS (
    SELECT MIN(gameweek_id) AS gw FROM dim_gameweek WHERE finished = 0
)
SELECT t.team_name,
       COUNT(*)                        AS fixtures_in_window,
       ROUND(AVG(tf.difficulty), 2)    AS avg_difficulty,
       SUM(tf.is_home)                 AS home_fixtures,
       GROUP_CONCAT(o.team_name, ', ') AS opponents
FROM fact_team_fixture tf
JOIN dim_team t ON t.team_id = tf.team_id
JOIN dim_team o ON o.team_id = tf.opponent_team_id
CROSS JOIN next_gw
WHERE tf.finished = 0
  AND tf.gameweek_id BETWEEN next_gw.gw AND next_gw.gw + 4
GROUP BY t.team_name
ORDER BY avg_difficulty ASC;