SELECT
    venue_name                       AS venue_name,
    COALESCE(city,    'Unknown')     AS city,
    COALESCE(country, 'Unknown')     AS country,
    capacity                         AS capacity
FROM venues
WHERE capacity > 50000
ORDER BY capacity DESC,
         venue_name ASC;