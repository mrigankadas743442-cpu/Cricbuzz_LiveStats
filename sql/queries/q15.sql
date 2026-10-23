-- Close = won by < 50 runs OR by < 5 wickets.
WITH close_matches AS (
    SELECT match_id, winner_id
    FROM matches
    WHERE winner_id IS NOT NULL
      AND (   (victory_type = 'runs'    AND victory_margin < 50)
           OR (victory_type = 'wickets' AND victory_margin < 5))
)
SELECT
    p.full_name                                  AS player_name,
    ROUND(AVG(b.runs), 2)                        AS avg_runs,
    COUNT(DISTINCT cm.match_id)                  AS close_matches_played,
    COUNT(DISTINCT CASE WHEN i.batting_team_id = cm.winner_id
                        THEN cm.match_id END)    AS close_matches_won
FROM close_matches cm
JOIN innings i            ON i.match_id   = cm.match_id
JOIN batting_scorecard b  ON b.innings_id = i.innings_id
JOIN players p            ON p.player_id  = b.player_id
GROUP BY p.player_id, p.full_name
ORDER BY avg_runs DESC, close_matches_won DESC;
