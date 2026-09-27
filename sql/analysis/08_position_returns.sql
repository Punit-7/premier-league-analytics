-- Q8: What does each position actually return, and at what price?
SELECT pos.position_name,
       COUNT(*)                                   AS players,
       ROUND(AVG(vp.price_m), 2)                  AS avg_price,
       ROUND(AVG(vp.points), 1)                   AS avg_points,
       ROUND(AVG(vp.points_per_million), 2)       AS avg_ppm,
       MAX(vp.points)                             AS best_points,
       pos.squad_select                           AS squad_slots
FROM player_season vp
JOIN dim_position pos ON pos.position_name = vp.position_name
WHERE vp.minutes >= 270
GROUP BY pos.position_name, pos.squad_select
ORDER BY avg_ppm DESC;