-- Q5: High returns at low ownership, the classic differential search.
SELECT web_name, team_name, position_short, price_m,
       points, points_per_million, selected_by_percent, minutes
FROM player_season
WHERE selected_by_percent < 5.0
  AND minutes >= 270
  AND points > 0
ORDER BY points_per_million DESC
LIMIT 25;