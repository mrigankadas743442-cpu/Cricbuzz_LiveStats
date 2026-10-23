SELECT
    t.team_name          AS team_name,
    COUNT(*)             AS total_wins
FROM matches m
JOIN teams t ON t.team_id = m.winner_id
WHERE m.winner_id IS NOT NULL
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC,
         t.team_name ASC;