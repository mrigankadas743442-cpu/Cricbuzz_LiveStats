-- Threshold relaxed from 5 to 2: the harvested data covers only a few weeks.
-- Restore 'HAVING COUNT(*) >= 5' once more history is loaded.
-- Category thresholds are a judgment call; tune them to your data.
WITH perf AS (
    SELECT b.player_id, b.runs, b.strike_rate,
           ROW_NUMBER() OVER (PARTITION BY b.player_id
                              ORDER BY m.match_date DESC, b.bat_id DESC) AS rn
    FROM batting_scorecard b
    JOIN innings i ON i.innings_id = b.innings_id
    JOIN matches m ON m.match_id   = i.match_id
),
agg AS (
    SELECT player_id,
           COUNT(*)                                          AS n,
           AVG(runs)                                         AS avg_last10,
           AVG(CASE WHEN rn <= 5 THEN runs END)              AS avg_last5,
           AVG(CASE WHEN rn <= 5 THEN strike_rate END)       AS sr_last5,
           AVG(CASE WHEN rn >  5 THEN strike_rate END)       AS sr_prev5,
           SUM(CASE WHEN runs >= 50 THEN 1 ELSE 0 END)       AS scores_50_plus,
           AVG(runs * runs) - AVG(runs) * AVG(runs)          AS variance
    FROM perf
    WHERE rn <= 10
    GROUP BY player_id
    HAVING COUNT(*) >= 2
)
SELECT
    p.full_name                         AS player_name,
    ROUND(a.avg_last5, 2)               AS avg_last_5,
    ROUND(a.avg_last10, 2)              AS avg_last_10,
    ROUND(a.sr_last5, 1)                AS sr_last_5,
    ROUND(a.sr_prev5, 1)                AS sr_previous_5,
    CASE WHEN a.sr_prev5 IS NULL THEN 'n/a'
         WHEN a.sr_last5 > a.sr_prev5 * 1.05 THEN 'Rising'
         WHEN a.sr_last5 < a.sr_prev5 * 0.95 THEN 'Falling'
         ELSE 'Steady' END              AS sr_trend,
    a.scores_50_plus                    AS scores_50_plus,
    ROUND(SQRT(MAX(a.variance, 0)), 2)  AS consistency_std_dev,
    CASE
        WHEN a.avg_last5 >= 50 AND a.scores_50_plus >= 3 THEN 'Excellent Form'
        WHEN a.avg_last5 >= 35                           THEN 'Good Form'
        WHEN a.avg_last5 >= 20                           THEN 'Average Form'
        ELSE 'Poor Form'
    END                                 AS form_category
FROM agg a
JOIN players p ON p.player_id = a.player_id
ORDER BY a.avg_last5 DESC;
