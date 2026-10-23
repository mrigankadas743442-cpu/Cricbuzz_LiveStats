SELECT
    series_name                          AS series_name,
    COALESCE(host_country, 'Unknown')    AS host_country,
    COALESCE(match_type,   'Unknown')    AS match_type,
    start_date                           AS start_date,
    total_matches                        AS total_matches
FROM series
WHERE start_date >= '2024-01-01'
  AND start_date <  '2025-01-01'
ORDER BY start_date ASC,
         series_name ASC;