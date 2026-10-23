SELECT
    COALESCE(playing_role, 'Not recorded')  AS playing_role,
    COUNT(*)                                AS player_count
FROM players
GROUP BY COALESCE(playing_role, 'Not recorded')
ORDER BY player_count DESC,
         playing_role ASC;