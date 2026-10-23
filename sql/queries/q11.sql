-- Overall average = total runs / total dismissals, where dismissals per format
-- are estimated as runs / batting_avg.
SELECT
    p.full_name AS player_name,
    SUM(CASE WHEN s.format = 'Test' THEN s.runs END) AS test_runs,
    SUM(CASE WHEN s.format = 'ODI'  THEN s.runs END) AS odi_runs,
    SUM(CASE WHEN s.format = 'T20I' THEN s.runs END) AS t20i_runs,
    ROUND(
        SUM(s.runs) * 1.0
        / NULLIF(SUM(s.runs * 1.0 / NULLIF(s.batting_avg, 0)), 0), 2
    ) AS overall_batting_avg
FROM player_career_stats s
JOIN players p ON p.player_id = s.player_id
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT s.format) >= 2
ORDER BY overall_batting_avg DESC;
