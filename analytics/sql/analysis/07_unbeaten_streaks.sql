-- Q7: Longest unbeaten streak per team per season (gaps and islands).
WITH tm AS (
    SELECT tm.team_id, tm.season_id, d.full_date,
           CASE WHEN tm.points > 0 THEN 1 ELSE 0 END AS unbeaten
    FROM team_match tm JOIN dim_date d ON d.date_id = tm.date_id
),
grouped AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY team_id, season_id ORDER BY full_date)
         - ROW_NUMBER() OVER (PARTITION BY team_id, season_id, unbeaten
                              ORDER BY full_date) AS island
    FROM tm
),
streaks AS (
    SELECT team_id, season_id, COUNT(*) AS streak_length,
           MIN(full_date) AS started, MAX(full_date) AS ended
    FROM grouped WHERE unbeaten = 1
    GROUP BY team_id, season_id, island
)
SELECT t.team_name, s.season_label, st.streak_length, st.started, st.ended
FROM streaks st
JOIN dim_team   t ON t.team_id   = st.team_id
JOIN dim_season s ON s.season_id = st.season_id
ORDER BY st.streak_length DESC LIMIT 15;