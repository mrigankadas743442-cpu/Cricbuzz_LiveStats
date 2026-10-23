CREATE VIEW IF NOT EXISTS v_match_details AS
SELECT m.match_id, m.description, m.match_format, m.match_date,
       t1.team_name AS team1, t2.team_name AS team2,
       v.venue_name, v.city, v.country AS venue_country,
       w.team_name AS winner, m.victory_margin, m.victory_type
FROM matches m
JOIN teams t1 ON t1.team_id = m.team1_id
JOIN teams t2 ON t2.team_id = m.team2_id
LEFT JOIN venues v ON v.venue_id = m.venue_id
LEFT JOIN teams w ON w.team_id = m.winner_id;

CREATE VIEW IF NOT EXISTS v_player_batting_summary AS
SELECT p.player_id, p.full_name, COUNT(*) AS innings,
       SUM(b.runs) AS total_runs, MAX(b.runs) AS highest_score,
       ROUND(SUM(b.runs) * 1.0 / NULLIF(SUM(b.is_out), 0), 2) AS batting_avg
FROM batting_scorecard b
JOIN players p ON p.player_id = b.player_id
GROUP BY p.player_id, p.full_name;

CREATE VIEW IF NOT EXISTS v_team_wins AS
SELECT t.team_name, COUNT(*) AS wins
FROM matches m
JOIN teams t ON t.team_id = m.winner_id
GROUP BY t.team_name;