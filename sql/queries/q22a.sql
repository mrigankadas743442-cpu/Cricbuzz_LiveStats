-- Threshold relaxed from 5 to 2: the harvested data covers only a few weeks.
-- Restore 'HAVING COUNT(*) >= 5' once more history is loaded.
WITH h2h AS (
    SELECT match_id,
           MIN(team1_id, team2_id) AS a,
           MAX(team1_id, team2_id) AS b,
           winner_id, victory_type, victory_margin
    FROM matches
    WHERE match_date >= date('now', '-3 years')
)
SELECT
    ta.team_name AS team_a,
    tb.team_name AS team_b,
    COUNT(*)     AS total_matches,
    SUM(h.winner_id = h.a) AS team_a_wins,
    SUM(h.winner_id = h.b) AS team_b_wins,
    ROUND(AVG(CASE WHEN h.winner_id = h.a AND h.victory_type = 'runs'    THEN h.victory_margin END), 1) AS a_avg_win_margin_runs,
    ROUND(AVG(CASE WHEN h.winner_id = h.a AND h.victory_type = 'wickets' THEN h.victory_margin END), 1) AS a_avg_win_margin_wkts,
    ROUND(AVG(CASE WHEN h.winner_id = h.b AND h.victory_type = 'runs'    THEN h.victory_margin END), 1) AS b_avg_win_margin_runs,
    ROUND(AVG(CASE WHEN h.winner_id = h.b AND h.victory_type = 'wickets' THEN h.victory_margin END), 1) AS b_avg_win_margin_wkts,
    ROUND(100.0 * SUM(h.winner_id = h.a) / COUNT(*), 1) AS team_a_win_pct,
    ROUND(100.0 * SUM(h.winner_id = h.b) / COUNT(*), 1) AS team_b_win_pct
FROM h2h h
JOIN teams ta ON ta.team_id = h.a
JOIN teams tb ON tb.team_id = h.b
GROUP BY h.a, h.b
HAVING COUNT(*) >= 2
ORDER BY total_matches DESC;
