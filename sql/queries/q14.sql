-- Threshold relaxed from 3 to 2: the harvested data covers only a few weeks.
-- Restore 'HAVING COUNT(DISTINCT m.match_id) >= 3' once more history is loaded.
SELECT
    p.full_name                       AS bowler,
    v.venue_name                      AS venue,
    COUNT(DISTINCT m.match_id)        AS matches_played,
    ROUND(AVG(bs.economy), 2)         AS avg_economy,
    SUM(bs.wickets)                   AS total_wickets
FROM bowling_scorecard bs
JOIN innings i ON i.innings_id = bs.innings_id
JOIN matches m ON m.match_id   = i.match_id
JOIN venues  v ON v.venue_id   = m.venue_id
JOIN players p ON p.player_id  = bs.player_id
WHERE bs.overs >= 4
GROUP BY p.player_id, p.full_name, v.venue_id, v.venue_name
HAVING COUNT(DISTINCT m.match_id) >= 2
ORDER BY avg_economy ASC, total_wickets DESC;
