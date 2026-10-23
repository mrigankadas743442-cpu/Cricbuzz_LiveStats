-- =====================================================================
-- Cricbuzz LiveStats: SQL Questions 9-25 (SQLite dialect)
-- Run each block separately. Blocks are marked with "-- ==== Qnn ====".
-- Notes:
--   * Q19 and Q23 use SQRT(). If you get "no such function: sqrt", register it:
--       conn.create_function("SQRT", 1, math.sqrt)
--   * Overs are stored as 9.4 meaning 9 overs + 4 balls, so Q18 converts to balls.
-- =====================================================================

-- ==== Q09 ==== All-rounders with > 1000 runs AND > 50 wickets (per format)
SELECT
    p.full_name        AS player_name,
    s.runs             AS total_runs,
    s.wickets          AS total_wickets,
    s.format           AS format
FROM player_career_stats s
JOIN players p ON p.player_id = s.player_id
WHERE p.playing_role = 'All-rounder'
  AND s.runs    > 1000
  AND s.wickets > 50
ORDER BY s.runs DESC, s.wickets DESC;

-- ==== Q10 ==== Last 20 completed matches
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

-- ==== Q11 ==== Runs per format + overall batting average (players with >= 2 formats)
-- Overall average = total runs / total dismissals, where dismissals per format
-- are estimated as runs / batting_avg.
SELECT
    p.full_name AS player_name,
    SUM(CASE WHEN s.format = 'Test' THEN s.runs END) AS test_runs,
    SUM(CASE WHEN s.format = 'ODI'  THEN s.runs END) AS odi_runs,
    SUM(CASE WHEN s.format = 'T20I' THEN s.runs END) AS t20i_runs,
    ROUND(
        SUM(s.runs) * 1.0
        / NULLIF(SUM(s.runs * 1.0 / NULLIF(s.batting_avg, 0)), 0), 2
    ) AS overall_batting_avg
FROM player_career_stats s
JOIN players p ON p.player_id = s.player_id
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT s.format) >= 2
ORDER BY overall_batting_avg DESC;

-- ==== Q12 ==== Home vs away wins per team
-- Home = venue country equals the winning team's country.
SELECT
    t.team_name AS team_name,
    SUM(CASE WHEN v.country =  t.country THEN 1 ELSE 0 END) AS home_wins,
    SUM(CASE WHEN v.country <> t.country THEN 1 ELSE 0 END) AS away_wins,
    COUNT(*)                                                AS total_wins
FROM matches m
JOIN teams  t ON t.team_id  = m.winner_id
JOIN venues v ON v.venue_id = m.venue_id
WHERE v.country IS NOT NULL
  AND t.country IS NOT NULL
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC, t.team_name;

-- ==== Q13 ==== Consecutive batsmen with a combined score >= 100 in an innings
SELECT
    pa.full_name                  AS batsman_1,
    pb.full_name                  AS batsman_2,
    b1.runs + b2.runs             AS combined_runs,
    m.description                 AS match_description,
    i.innings_no                  AS innings_no,
    b1.batting_position           AS position_1,
    b2.batting_position           AS position_2
FROM batting_scorecard b1
JOIN batting_scorecard b2
      ON b2.innings_id       = b1.innings_id
     AND b2.batting_position = b1.batting_position + 1
JOIN innings i  ON i.innings_id = b1.innings_id
JOIN matches m  ON m.match_id   = i.match_id
JOIN players pa ON pa.player_id = b1.player_id
JOIN players pb ON pb.player_id = b2.player_id
WHERE b1.runs + b2.runs >= 100
ORDER BY combined_runs DESC;

-- ==== Q14 ==== Bowling at venues (>= 3 matches at a venue, >= 4 overs each match counted)
SELECT
    p.full_name                       AS bowler,
    v.venue_name                      AS venue,
    COUNT(DISTINCT m.match_id)        AS matches_played,
    ROUND(AVG(bs.economy), 2)         AS avg_economy,
    SUM(bs.wickets)                   AS total_wickets
FROM bowling_scorecard bs
JOIN innings i ON i.innings_id = bs.innings_id
JOIN matches m ON m.match_id   = i.match_id
JOIN venues  v ON v.venue_id   = m.venue_id
JOIN players p ON p.player_id  = bs.player_id
WHERE bs.overs >= 4
GROUP BY p.player_id, p.full_name, v.venue_id, v.venue_name
HAVING COUNT(DISTINCT m.match_id) >= 3
ORDER BY avg_economy ASC, total_wickets DESC;

-- ==== Q15 ==== Performance in close matches
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

-- ==== Q16 ==== Yearly batting trend since 2020 (>= 5 matches in that year)
SELECT
    p.full_name                                              AS player_name,
    strftime('%Y', m.match_date)                             AS year,
    COUNT(DISTINCT m.match_id)                               AS matches,
    ROUND(SUM(b.runs) * 1.0 / COUNT(DISTINCT m.match_id), 2) AS avg_runs_per_match,
    ROUND(AVG(b.strike_rate), 2)                             AS avg_strike_rate
FROM batting_scorecard b
JOIN innings i ON i.innings_id = b.innings_id
JOIN matches m ON m.match_id   = i.match_id
JOIN players p ON p.player_id  = b.player_id
WHERE m.match_date >= '2020-01-01'
GROUP BY p.player_id, p.full_name, strftime('%Y', m.match_date)
HAVING COUNT(DISTINCT m.match_id) >= 5
ORDER BY p.full_name, year;

-- ==== Q17 ==== Does winning the toss help?
SELECT
    toss_decision AS toss_decision,
    COUNT(*)      AS matches,
    SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) AS toss_winner_won,
    ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS win_pct
FROM matches
WHERE toss_winner_id IS NOT NULL
  AND winner_id      IS NOT NULL
  AND toss_decision  IS NOT NULL
GROUP BY toss_decision
UNION ALL
SELECT
    'overall',
    COUNT(*),
    SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END)
          / COUNT(*), 2)
FROM matches
WHERE toss_winner_id IS NOT NULL
  AND winner_id      IS NOT NULL
  AND toss_decision  IS NOT NULL;

-- ==== Q18 ==== Most economical bowlers in ODI and T20I
-- Economy = runs * 6 / balls. Overs like 9.4 are converted to 9*6 + 4 = 58 balls.
WITH spells AS (
    SELECT
        bs.player_id,
        m.match_id,
        bs.runs_conceded,
        bs.wickets,
        CAST(bs.overs AS INTEGER) * 6
          + CAST(ROUND((bs.overs - CAST(bs.overs AS INTEGER)) * 10) AS INTEGER) AS balls
    FROM bowling_scorecard bs
    JOIN innings i ON i.innings_id = bs.innings_id
    JOIN matches m ON m.match_id   = i.match_id
    WHERE m.match_format IN ('ODI', 'T20I')
)
SELECT
    p.full_name                               AS bowler,
    COUNT(DISTINCT s.match_id)                AS matches_bowled,
    ROUND(SUM(s.balls) / 6.0, 1)              AS total_overs,
    ROUND(SUM(s.runs_conceded) * 6.0 / SUM(s.balls), 2) AS economy_rate,
    SUM(s.wickets)                            AS total_wickets
FROM spells s
JOIN players p ON p.player_id = s.player_id
WHERE s.balls > 0
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT s.match_id) >= 10
   AND SUM(s.balls) / 6.0 / COUNT(DISTINCT s.match_id) >= 2
ORDER BY economy_rate ASC, total_wickets DESC;

-- ==== Q19 ==== Most consistent batsmen (lowest std deviation), since 2022
-- Population std dev = sqrt(E[x^2] - E[x]^2). Innings with < 10 balls are ignored.
-- HAVING >= 3 innings is an added guard: one innings always has std dev 0.
SELECT
    p.full_name                            AS player_name,
    COUNT(*)                               AS innings,
    ROUND(AVG(b.runs), 2)                  AS avg_runs,
    ROUND(SQRT(MAX(AVG(b.runs * b.runs) - AVG(b.runs) * AVG(b.runs), 0)), 2)
                                           AS std_dev_runs
FROM batting_scorecard b
JOIN innings i ON i.innings_id = b.innings_id
JOIN matches m ON m.match_id   = i.match_id
JOIN players p ON p.player_id  = b.player_id
WHERE b.balls >= 10
  AND m.match_date >= '2022-01-01'
GROUP BY p.player_id, p.full_name
HAVING COUNT(*) >= 3
ORDER BY std_dev_runs ASC, avg_runs DESC;

-- ==== Q20 ==== Matches and batting average per format (>= 20 total matches)
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

-- ==== Q21 ==== Weighted performance ranking, top 10 per format
WITH field AS (
    SELECT f.player_id, m.match_format AS format,
           SUM(f.catches) AS catches, SUM(f.stumpings) AS stumpings
    FROM fielding_stats f
    JOIN matches m ON m.match_id = f.match_id
    GROUP BY f.player_id, m.match_format
),
scored AS (
    SELECT
        p.full_name AS player_name,
        s.format    AS format,
        COALESCE(s.runs, 0) * 0.01
          + COALESCE(s.batting_avg, 0) * 0.5
          + COALESCE(s.strike_rate, 0) * 0.3                      AS batting_pts,
        CASE WHEN COALESCE(s.wickets, 0) > 0
             THEN s.wickets * 2
                  + (50 - COALESCE(s.bowling_avg, 50)) * 0.5
                  + (6  - COALESCE(s.economy, 6)) * 2
             ELSE 0 END                                           AS bowling_pts,
        COALESCE(f.catches, 0) * 3 + COALESCE(f.stumpings, 0) * 5 AS fielding_pts
    FROM player_career_stats s
    JOIN players p ON p.player_id = s.player_id
    LEFT JOIN field f ON f.player_id = s.player_id AND f.format = s.format
),
totals AS (
    SELECT *, batting_pts + bowling_pts + fielding_pts AS total_points
    FROM scored
),
ranked AS (
    SELECT *, RANK() OVER (PARTITION BY format ORDER BY total_points DESC) AS rnk
    FROM totals
)
SELECT format, rnk AS rank, player_name,
       ROUND(batting_pts, 2)  AS batting_pts,
       ROUND(bowling_pts, 2)  AS bowling_pts,
       ROUND(fielding_pts, 2) AS fielding_pts,
       ROUND(total_points, 2) AS total_points
FROM ranked
WHERE rnk <= 10
ORDER BY format, rnk;

-- ==== Q22a ==== Head-to-head summary (pairs with >= 5 matches in the last 3 years)
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
HAVING COUNT(*) >= 5
ORDER BY total_matches DESC;

-- ==== Q22b ==== Same pairs: batting first vs bowling first, by venue
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
    HAVING COUNT(*) >= 5
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

-- ==== Q23 ==== Recent form (last 10 batting performances per player)
-- Category thresholds are a judgment call; tune them to your data.
WITH perf AS (
    SELECT b.player_id, b.runs, b.strike_rate,
           ROW_NUMBER() OVER (PARTITION BY b.player_id
                              ORDER BY m.match_date DESC, b.bat_id DESC) AS rn
    FROM batting_scorecard b
    JOIN innings i ON i.innings_id = b.innings_id
    JOIN matches m ON m.match_id   = i.match_id
),
agg AS (
    SELECT player_id,
           COUNT(*)                                          AS n,
           AVG(runs)                                         AS avg_last10,
           AVG(CASE WHEN rn <= 5 THEN runs END)              AS avg_last5,
           AVG(CASE WHEN rn <= 5 THEN strike_rate END)       AS sr_last5,
           AVG(CASE WHEN rn >  5 THEN strike_rate END)       AS sr_prev5,
           SUM(CASE WHEN runs >= 50 THEN 1 ELSE 0 END)       AS scores_50_plus,
           AVG(runs * runs) - AVG(runs) * AVG(runs)          AS variance
    FROM perf
    WHERE rn <= 10
    GROUP BY player_id
    HAVING COUNT(*) >= 5
)
SELECT
    p.full_name                         AS player_name,
    ROUND(a.avg_last5, 2)               AS avg_last_5,
    ROUND(a.avg_last10, 2)              AS avg_last_10,
    ROUND(a.sr_last5, 1)                AS sr_last_5,
    ROUND(a.sr_prev5, 1)                AS sr_previous_5,
    CASE WHEN a.sr_prev5 IS NULL THEN 'n/a'
         WHEN a.sr_last5 > a.sr_prev5 * 1.05 THEN 'Rising'
         WHEN a.sr_last5 < a.sr_prev5 * 0.95 THEN 'Falling'
         ELSE 'Steady' END              AS sr_trend,
    a.scores_50_plus                    AS scores_50_plus,
    ROUND(SQRT(MAX(a.variance, 0)), 2)  AS consistency_std_dev,
    CASE
        WHEN a.avg_last5 >= 50 AND a.scores_50_plus >= 3 THEN 'Excellent Form'
        WHEN a.avg_last5 >= 35                           THEN 'Good Form'
        WHEN a.avg_last5 >= 20                           THEN 'Average Form'
        ELSE 'Poor Form'
    END                                 AS form_category
FROM agg a
JOIN players p ON p.player_id = a.player_id
ORDER BY a.avg_last5 DESC;

-- ==== Q24 ==== Best batting partnerships (consecutive positions, >= 5 partnerships)
-- Partnership runs = sum of the two batsmen's individual scores (see Q13 note).
-- "Good partnership" = more than 50 runs.
WITH pship AS (
    SELECT MIN(b1.player_id, b2.player_id) AS p1,
           MAX(b1.player_id, b2.player_id) AS p2,
           b1.runs + b2.runs               AS runs
    FROM batting_scorecard b1
    JOIN batting_scorecard b2
          ON b2.innings_id       = b1.innings_id
         AND b2.batting_position = b1.batting_position + 1
)
SELECT
    pa.full_name                                   AS player_1,
    pb.full_name                                   AS player_2,
    COUNT(*)                                       AS partnerships,
    ROUND(AVG(ps.runs), 1)                         AS avg_partnership_runs,
    SUM(CASE WHEN ps.runs > 50 THEN 1 ELSE 0 END)  AS partnerships_over_50,
    MAX(ps.runs)                                   AS highest_partnership,
    ROUND(100.0 * SUM(CASE WHEN ps.runs > 50 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                   AS success_rate_pct
FROM pship ps
JOIN players pa ON pa.player_id = ps.p1
JOIN players pb ON pb.player_id = ps.p2
GROUP BY ps.p1, ps.p2
HAVING COUNT(*) >= 5
ORDER BY success_rate_pct DESC, avg_partnership_runs DESC;

-- ==== Q25a ==== Quarterly batting averages with change vs previous quarter
-- Only quarters with >= 3 matches count; players need >= 6 such quarters.
-- Change labels use a +/-10% band on average runs.
WITH q AS (
    SELECT b.player_id,
           strftime('%Y', m.match_date) || '-Q' ||
             ((CAST(strftime('%m', m.match_date) AS INTEGER) + 2) / 3) AS qtr,
           COUNT(DISTINCT m.match_id) AS matches,
           AVG(b.runs)                AS avg_runs,
           AVG(b.strike_rate)         AS avg_sr
    FROM batting_scorecard b
    JOIN innings i ON i.innings_id = b.innings_id
    JOIN matches m ON m.match_id   = i.match_id
    GROUP BY b.player_id, qtr
    HAVING COUNT(DISTINCT m.match_id) >= 3
),
eligible AS (
    SELECT player_id FROM q GROUP BY player_id HAVING COUNT(*) >= 6
),
chg AS (
    SELECT q.*,
           LAG(avg_runs) OVER (PARTITION BY player_id ORDER BY qtr) AS prev_runs,
           LAG(avg_sr)   OVER (PARTITION BY player_id ORDER BY qtr) AS prev_sr
    FROM q
    WHERE player_id IN (SELECT player_id FROM eligible)
)
SELECT
    p.full_name                  AS player_name,
    c.qtr                        AS quarter,
    c.matches                    AS matches,
    ROUND(c.avg_runs, 2)         AS avg_runs,
    ROUND(c.avg_sr, 1)           AS avg_strike_rate,
    CASE WHEN c.prev_runs IS NULL        THEN 'First quarter'
         WHEN c.avg_runs > c.prev_runs * 1.1 THEN 'Improving'
         WHEN c.avg_runs < c.prev_runs * 0.9 THEN 'Declining'
         ELSE 'Stable' END       AS vs_previous_quarter
FROM chg c
JOIN players p ON p.player_id = c.player_id
ORDER BY p.full_name, c.qtr;

-- ==== Q25b ==== Career phase: first 3 qualifying quarters vs last 3
WITH q AS (
    SELECT b.player_id,
           strftime('%Y', m.match_date) || '-Q' ||
             ((CAST(strftime('%m', m.match_date) AS INTEGER) + 2) / 3) AS qtr,
           AVG(b.runs) AS avg_runs
    FROM batting_scorecard b
    JOIN innings i ON i.innings_id = b.innings_id
    JOIN matches m ON m.match_id   = i.match_id
    GROUP BY b.player_id, qtr
    HAVING COUNT(DISTINCT m.match_id) >= 3
),
numbered AS (
    SELECT player_id, qtr, avg_runs,
           ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY qtr) AS rn,
           COUNT(*)     OVER (PARTITION BY player_id)              AS cnt
    FROM q
),
phase AS (
    SELECT player_id,
           MAX(cnt) AS quarters,
           AVG(CASE WHEN rn <= 3       THEN avg_runs END) AS early_avg,
           AVG(CASE WHEN rn >  cnt - 3 THEN avg_runs END) AS recent_avg
    FROM numbered
    GROUP BY player_id
    HAVING MAX(cnt) >= 6
)
SELECT
    p.full_name               AS player_name,
    ph.quarters               AS quarters_analysed,
    ROUND(ph.early_avg, 2)    AS early_avg_runs,
    ROUND(ph.recent_avg, 2)   AS recent_avg_runs,
    CASE WHEN ph.recent_avg > ph.early_avg * 1.1 THEN 'Career Ascending'
         WHEN ph.recent_avg < ph.early_avg * 0.9 THEN 'Career Declining'
         ELSE 'Career Stable' END AS career_phase
FROM phase ph
JOIN players p ON p.player_id = ph.player_id
ORDER BY ph.recent_avg - ph.early_avg DESC;