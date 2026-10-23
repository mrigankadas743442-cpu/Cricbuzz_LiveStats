-- Threshold relaxed for small data: the brief asks for QUARTERS (>= 3 matches
-- each, players with >= 6 quarters). Harvested data covers only a few weeks,
-- so this version uses calendar WEEKS, >= 1 match per week, players with
-- >= 2 weeks. Change labels use a +/-10% band on average runs.
WITH q AS (
    SELECT b.player_id,
           strftime('%Y-W%W', m.match_date) AS period,
           COUNT(DISTINCT m.match_id) AS matches,
           AVG(b.runs)                AS avg_runs,
           AVG(b.strike_rate)         AS avg_sr
    FROM batting_scorecard b
    JOIN innings i ON i.innings_id = b.innings_id
    JOIN matches m ON m.match_id   = i.match_id
    GROUP BY b.player_id, period
    HAVING COUNT(DISTINCT m.match_id) >= 1
),
eligible AS (
    SELECT player_id FROM q GROUP BY player_id HAVING COUNT(*) >= 2
),
chg AS (
    SELECT q.*,
           LAG(avg_runs) OVER (PARTITION BY player_id ORDER BY period) AS prev_runs,
           LAG(avg_sr)   OVER (PARTITION BY player_id ORDER BY period) AS prev_sr
    FROM q
    WHERE player_id IN (SELECT player_id FROM eligible)
)
SELECT
    p.full_name                  AS player_name,
    c.period                     AS period,
    c.matches                    AS matches,
    ROUND(c.avg_runs, 2)         AS avg_runs,
    ROUND(c.avg_sr, 1)           AS avg_strike_rate,
    CASE WHEN c.prev_runs IS NULL        THEN 'First period'
         WHEN c.avg_runs > c.prev_runs * 1.1 THEN 'Improving'
         WHEN c.avg_runs < c.prev_runs * 0.9 THEN 'Declining'
         ELSE 'Stable' END       AS vs_previous_period
FROM chg c
JOIN players p ON p.player_id = c.player_id
ORDER BY p.full_name, c.period;