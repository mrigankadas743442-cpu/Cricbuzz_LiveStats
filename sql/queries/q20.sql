SELECT
    p.full_name AS player_name,
    MAX(CASE WHEN s.format = 'Test' THEN s.matches_played END) AS test_matches,
    MAX(CASE WHEN s.format = 'ODI'  THEN s.matches_played END) AS odi_matches,
    MAX(CASE WHEN s.format = 'T20I' THEN s.matches_played END) AS t20i_matches,
    MAX(CASE WHEN s.format = 'Test' THEN s.batting_avg END)    AS test_avg,
    MAX(CASE WHEN s.format = 'ODI'  THEN s.batting_avg END)    AS odi_avg,
    MAX(CASE WHEN s.format = 'T20I' THEN s.batting_avg END)    AS t20i_avg,
    SUM(s.matches_played)                                      AS total_matches
FROM player_career_stats s
JOIN players p ON p.player_id = s.player_id
GROUP BY p.player_id, p.full_name
HAVING SUM(s.matches_played) >= 20
ORDER BY total_matches DESC;
