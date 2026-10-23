SELECT
    full_name                              AS player_name,
    COALESCE(playing_role,  'Not recorded') AS playing_role,
    COALESCE(batting_style, 'Not recorded') AS batting_style,
    COALESCE(bowling_style, 'Not recorded') AS bowling_style
FROM players
WHERE country = 'India'
ORDER BY full_name;