-- Q9: Is 2026/27 unusual, or is this just a small sample?
WITH by_season AS (
    SELECT s.season_label, s.status, COUNT(*) AS matches,
           1.0*SUM(CASE WHEN f.ft_result='H' THEN 1 ELSE 0 END)/COUNT(*) AS home_win_rate,
           AVG(f.total_goals) AS goals_per_game
    FROM fact_match f JOIN dim_season s ON s.season_id = f.season_id
    GROUP BY s.season_label, s.status
),
baseline AS (
    SELECT AVG(home_win_rate) AS hw, AVG(goals_per_game) AS gpg
    FROM by_season WHERE status = 'completed'
)
SELECT b.season_label, b.status, b.matches,
       ROUND(100*b.home_win_rate, 1)              AS home_win_pct,
       ROUND(100*(b.home_win_rate - x.hw), 1)     AS vs_baseline_pts,
       ROUND(b.goals_per_game, 2)                 AS goals_per_game,
       ROUND(b.goals_per_game - x.gpg, 2)         AS goals_vs_baseline
FROM by_season b CROSS JOIN baseline x
ORDER BY b.season_label;