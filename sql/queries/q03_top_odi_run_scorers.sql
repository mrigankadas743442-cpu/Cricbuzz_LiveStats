SELECT
    p.full_name                          AS player_name,
    s.runs                               AS total_runs,
    ROUND(s.batting_avg, 2)              AS batting_average,
    s.centuries                          AS centuries
FROM player_career_stats s
JOIN players p ON p.player_id = s.player_id
WHERE s.format = 'ODI'
  AND s.runs IS NOT NULL
ORDER BY s.runs DESC,
         s.batting_avg DESC,
         p.full_name ASC
LIMIT 10;