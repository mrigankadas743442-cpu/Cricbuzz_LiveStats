-- Threshold relaxed from 10 to 2: the harvested data covers only a few weeks.
-- Restore 'HAVING COUNT(DISTINCT s.match_id) >= 10' once more history is loaded.
-- Economy = runs * 6 / balls. Overs like 9.4 are converted to 9*6 + 4 = 58 balls.
WITH spells AS (
    SELECT
        bs.player_id,
        m.match_id,
        bs.runs_conceded,
        bs.wickets,
        CAST(bs.overs AS INTEGER) * 6
          + CAST(ROUND((bs.overs - CAST(bs.overs AS INTEGER)) * 10) AS INTEGER) AS balls
    FROM bowling_scorecard bs
    JOIN innings i ON i.innings_id = bs.innings_id
    JOIN matches m ON m.match_id   = i.match_id
    WHERE m.match_format IN ('ODI', 'T20I')
)
SELECT
    p.full_name                               AS bowler,
    COUNT(DISTINCT s.match_id)                AS matches_bowled,
    ROUND(SUM(s.balls) / 6.0, 1)              AS total_overs,
    ROUND(SUM(s.runs_conceded) * 6.0 / SUM(s.balls), 2) AS economy_rate,
    SUM(s.wickets)                            AS total_wickets
FROM spells s
JOIN players p ON p.player_id = s.player_id
WHERE s.balls > 0
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT s.match_id) >= 2
   AND SUM(s.balls) / 6.0 / COUNT(DISTINCT s.match_id) >= 2
ORDER BY economy_rate ASC, total_wickets DESC;
