SELECT
    p.full_name  AS player_name,
    s.runs       AS total_runs,
    s.wickets    AS total_wickets,
    s.format     AS format
FROM player_career_stats s
JOIN players p ON p.player_id = s.player_id
WHERE s.runs    > 1000
  AND s.wickets > 50
ORDER BY s.runs DESC, s.wickets DESC;
