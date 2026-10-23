-- Threshold relaxed from 5 to 2: the harvested data covers only a few weeks.
-- Restore 'HAVING COUNT(*) >= 5' once more history is loaded.
WITH base AS (
    SELECT m.match_id, m.team1_id AS t1, m.team2_id AS t2,
           m.winner_id, m.venue_id,
           (SELECT i.batting_team_id FROM innings i
             WHERE i.match_id = m.match_id AND i.innings_no = 1) AS first_bat
    FROM matches m
    WHERE m.match_date >= date('now', '-3 years')
),
qual AS (
    SELECT MIN(t1, t2) AS a, MAX(t1, t2) AS b
    FROM base
    GROUP BY MIN(t1, t2), MAX(t1, t2)
    HAVING COUNT(*) >= 2
),
persp AS (
    SELECT match_id, t1 AS team, t2 AS opp, winner_id, venue_id, first_bat FROM base
    UNION ALL
    SELECT match_id, t2 AS team, t1 AS opp, winner_id, venue_id, first_bat FROM base
)
SELECT
    t.team_name                                   AS team,
    o.team_name                                   AS opponent,
    COALESCE(v.venue_name, 'Unknown')             AS venue,
    SUM(p.first_bat = p.team)                     AS matches_batting_first,
    SUM(p.first_bat = p.team AND p.winner_id = p.team) AS wins_batting_first,
    SUM(p.first_bat <> p.team)                    AS matches_bowling_first,
    SUM(p.first_bat <> p.team AND p.winner_id = p.team) AS wins_bowling_first
FROM persp p
JOIN qual q ON q.a = MIN(p.team, p.opp) AND q.b = MAX(p.team, p.opp)
JOIN teams t ON t.team_id = p.team
JOIN teams o ON o.team_id = p.opp
LEFT JOIN venues v ON v.venue_id = p.venue_id
WHERE p.first_bat IS NOT NULL
GROUP BY p.team, p.opp, p.venue_id
ORDER BY team, opponent, venue;
