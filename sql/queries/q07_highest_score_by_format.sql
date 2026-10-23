SELECT
    format                  AS format,
    MAX(highest_score)      AS highest_score
FROM player_career_stats
WHERE highest_score IS NOT NULL
GROUP BY format
ORDER BY CASE format
             WHEN 'Test' THEN 1
             WHEN 'ODI'  THEN 2
             WHEN 'T20I' THEN 3
         END;