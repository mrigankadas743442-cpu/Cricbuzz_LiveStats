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
