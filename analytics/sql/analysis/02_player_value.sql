-- Q2: Which players return the most points per pound of budget?
SELECT web_name, team_name, position_short,
       price_m, points, points_per_million,
       appearances, minutes, selected_by_percent
FROM player_season
WHERE minutes >= 270          -- three full matches; filters out noise
ORDER BY points_per_million DESC
LIMIT 30;