-- Population std dev = sqrt(E[x^2] - E[x]^2). Innings with < 10 balls are ignored.
-- HAVING >= 3 innings is an added guard: one innings always has std dev 0.
SELECT
    p.full_name                            AS player_name,
    COUNT(*)                               AS innings,
    ROUND(AVG(b.runs), 2)                  AS avg_runs,
    ROUND(SQRT(MAX(AVG(b.runs * b.runs) - AVG(b.runs) * AVG(b.runs), 0)), 2)
                                           AS std_dev_runs
FROM batting_scorecard b
JOIN innings i ON i.innings_id = b.innings_id
JOIN matches m ON m.match_id   = i.match_id
JOIN players p ON p.player_id  = b.player_id
WHERE b.balls >= 10
  AND m.match_date >= '2022-01-01'
GROUP BY p.player_id, p.full_name
HAVING COUNT(*) >= 3
ORDER BY std_dev_runs ASC, avg_runs DESC;
