-- Home = venue country equals the winning team's country.
SELECT
    t.team_name AS team_name,
    SUM(CASE WHEN v.country =  t.country THEN 1 ELSE 0 END) AS home_wins,
    SUM(CASE WHEN v.country <> t.country THEN 1 ELSE 0 END) AS away_wins,
    COUNT(*)                                                AS total_wins
FROM matches m
JOIN teams  t ON t.team_id  = m.winner_id
JOIN venues v ON v.venue_id = m.venue_id
WHERE v.country IS NOT NULL
  AND t.country IS NOT NULL
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC, t.team_name;
