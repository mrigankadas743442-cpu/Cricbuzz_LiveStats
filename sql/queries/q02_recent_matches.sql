SELECT
    m.description                            AS match_description,
    t1.team_name                             AS team_1,
    t2.team_name                             AS team_2,
    v.venue_name || COALESCE(', ' || v.city, '') AS venue,
    m.match_date                             AS match_date
FROM matches m
JOIN teams t1       ON t1.team_id  = m.team1_id
JOIN teams t2       ON t2.team_id  = m.team2_id
LEFT JOIN venues v  ON v.venue_id  = m.venue_id
WHERE m.match_date BETWEEN date('now', '-30 days') AND date('now')
ORDER BY m.match_date DESC, m.match_id DESC;