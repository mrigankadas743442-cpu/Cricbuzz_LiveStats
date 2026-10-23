-- Threshold relaxed from 5 to 2: the harvested data covers only a few weeks.
-- Restore 'HAVING COUNT(*) >= 5' once more history is loaded.
-- Partnership runs = sum of the two batsmen's individual scores (see Q13 note).
-- "Good partnership" = more than 50 runs.
WITH pship AS (
    SELECT MIN(b1.player_id, b2.player_id) AS p1,
           MAX(b1.player_id, b2.player_id) AS p2,
           b1.runs + b2.runs               AS runs
    FROM batting_scorecard b1
    JOIN batting_scorecard b2
          ON b2.innings_id       = b1.innings_id
         AND b2.batting_position = b1.batting_position + 1
)
SELECT
    pa.full_name                                   AS player_1,
    pb.full_name                                   AS player_2,
    COUNT(*)                                       AS partnerships,
    ROUND(AVG(ps.runs), 1)                         AS avg_partnership_runs,
    SUM(CASE WHEN ps.runs > 50 THEN 1 ELSE 0 END)  AS partnerships_over_50,
    MAX(ps.runs)                                   AS highest_partnership,
    ROUND(100.0 * SUM(CASE WHEN ps.runs > 50 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                   AS success_rate_pct
FROM pship ps
JOIN players pa ON pa.player_id = ps.p1
JOIN players pb ON pb.player_id = ps.p2
GROUP BY ps.p1, ps.p2
HAVING COUNT(*) >= 2
ORDER BY success_rate_pct DESC, avg_partnership_runs DESC;
