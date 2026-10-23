SELECT
    m.description                         AS match_description,
    t1.team_name                          AS team_1,
    t2.team_name                          AS team_2,
    COALESCE(w.team_name, 'No result')    AS winning_team,
    m.victory_margin                      AS victory_margin,
    m.victory_type                        AS victory_type,
    COALESCE(v.venue_name, 'Unknown')     AS venue,
    m.match_date                          AS match_date
FROM matches m
JOIN teams t1      ON t1.team_id = m.team1_id
JOIN teams t2      ON t2.team_id = m.team2_id
LEFT JOIN teams w  ON w.team_id  = m.winner_id
LEFT JOIN venues v ON v.venue_id = m.venue_id
WHERE m.winner_id IS NOT NULL
   OR m.victory_type IN ('draw', 'tie')
ORDER BY m.match_date DESC, m.match_id DESC
LIMIT 20;
