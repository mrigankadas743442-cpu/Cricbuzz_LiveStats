SELECT
    toss_decision AS toss_decision,
    COUNT(*)      AS matches,
    SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) AS toss_winner_won,
    ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS win_pct
FROM matches
WHERE toss_winner_id IS NOT NULL
  AND winner_id      IS NOT NULL
  AND toss_decision  IS NOT NULL
GROUP BY toss_decision
UNION ALL
SELECT
    'overall',
    COUNT(*),
    SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END)
          / COUNT(*), 2)
FROM matches
WHERE toss_winner_id IS NOT NULL
  AND winner_id      IS NOT NULL
  AND toss_decision  IS NOT NULL;
