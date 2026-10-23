-- Threshold relaxed from 5 to 2: the harvested data covers only a few weeks.
-- Restore 'HAVING COUNT(DISTINCT m.match_id) >= 5' once more history is loaded.
SELECT
    p.full_name                                              AS player_name,
    strftime('%Y', m.match_date)                             AS year,
    COUNT(DISTINCT m.match_id)                               AS matches,
    ROUND(SUM(b.runs) * 1.0 / COUNT(DISTINCT m.match_id), 2) AS avg_runs_per_match,
    ROUND(AVG(b.strike_rate), 2)                             AS avg_strike_rate
FROM batting_scorecard b
JOIN innings i ON i.innings_id = b.innings_id
JOIN matches m ON m.match_id   = i.match_id
JOIN players p ON p.player_id  = b.player_id
WHERE m.match_date >= '2020-01-01'
GROUP BY p.player_id, p.full_name, strftime('%Y', m.match_date)
HAVING COUNT(DISTINCT m.match_id) >= 2
ORDER BY p.full_name, year;
