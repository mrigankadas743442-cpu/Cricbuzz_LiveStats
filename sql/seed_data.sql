INSERT INTO teams (team_id, team_name, short_name, country) VALUES
 (1,'India','IND','India'), (2,'Australia','AUS','Australia'),
 (3,'England','ENG','England'), (4,'Pakistan','PAK','Pakistan');

INSERT INTO venues (venue_id, venue_name, city, country, capacity) VALUES
 (1,'Sample Stadium A','Ahmedabad','India',130000),
 (2,'Sample Stadium B','Melbourne','Australia',100000),
 (3,'Sample Ground C','Mumbai','India',33000);

INSERT INTO players (player_id, full_name, country, team_id, playing_role, batting_style, bowling_style) VALUES
 (1,'Sample Player One','India',1,'Batsman','Right-hand bat','Right-arm medium'),
 (2,'Sample Player Two','India',1,'Bowler','Right-hand bat','Right-arm fast'),
 (3,'Sample Player Three','Australia',2,'All-rounder','Left-hand bat','Left-arm spin'),
 (4,'Sample Player Four','Australia',2,'Wicket-keeper','Left-hand bat',NULL),
 (5,'Sample Player Five','England',3,'Batsman','Right-hand bat','Right-arm off-break'),
 (6,'Sample Player Six','India',1,'All-rounder','Right-hand bat','Right-arm medium');

INSERT INTO series (series_id, series_name, host_country, match_type, start_date, total_matches) VALUES
 (1,'Sample ODI Series','India','ODI','2024-01-10',3);

INSERT INTO matches (match_id, series_id, description, match_format, team1_id, team2_id,
                     venue_id, match_date, status, toss_winner_id, toss_decision,
                     winner_id, victory_margin, victory_type) VALUES
 (1,1,'1st ODI','ODI',1,2,1,date('now','-5 days'),'Complete',2,'bowl',1,6,'wickets'),
 (2,1,'2nd ODI','ODI',2,3,2,date('now','-60 days'),'Complete',2,'bat',2,20,'runs');

INSERT INTO innings (innings_id, match_id, innings_no, batting_team_id, total_runs, wickets, overs) VALUES
 (1,1,1,2,250,10,49.2), (2,1,2,1,251,4,46.0),
 (3,2,1,2,300,6,50.0),  (4,2,2,3,280,10,48.4);

INSERT INTO batting_scorecard (innings_id, player_id, batting_position, runs, balls, fours, sixes, strike_rate, is_out) VALUES
 (1,3,1,60,70,6,1,85.7,1), (1,4,2,45,50,4,0,90.0,1),
 (2,1,1,95,100,8,2,95.0,1), (2,6,2,70,65,5,3,107.7,0),
 (3,3,1,110,105,9,3,104.8,1), (3,4,2,52,48,5,1,108.3,1),
 (4,5,1,88,90,7,2,97.8,1);

INSERT INTO bowling_scorecard (innings_id, player_id, overs, maidens, runs_conceded, wickets, economy) VALUES
 (1,2,10,1,48,3,4.8), (1,6,8,0,40,2,5.0),
 (4,3,10,0,55,4,5.5);

 INSERT INTO player_career_stats
    (player_id, format, matches_played, runs, highest_score, batting_avg, strike_rate, centuries)
VALUES
 (1,'ODI',250,12000,183,57.3,93.2,40),
 (2,'ODI',100, 1500, 70,18.5,78.0, 0),
 (3,'ODI',180, 6500,140,42.1,88.4,12),
 (4,'ODI',120, 3900,120,35.2,95.0, 5),
 (5,'ODI',200, 8800,160,48.9,90.1,22);

 INSERT INTO player_career_stats
    (player_id, format, matches_played, runs, highest_score, batting_avg, strike_rate, centuries)
VALUES
 (1,'Test',100,8000,254,50.1,55.0,25),
 (3,'T20I', 90,2500,122,36.0,140.5, 2);

 INSERT INTO series (series_name, host_country, match_type, start_date, total_matches) VALUES
 ('Sample T20I Series','Australia','T20I','2024-12-31',3),
 ('Sample Test Series','England','Test','2025-01-01',5),
 ('Sample ODI Series','India','ODI','2023-12-31',3);