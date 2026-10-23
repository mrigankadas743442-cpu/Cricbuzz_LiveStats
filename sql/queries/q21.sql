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
