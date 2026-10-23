
CREATE TABLE teams (
    team_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    cb_team_id  INTEGER UNIQUE,
    team_name   TEXT NOT NULL UNIQUE,
    short_name  TEXT,
    country     TEXT NOT NULL
);

CREATE TABLE players (
    player_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    cb_player_id  INTEGER UNIQUE,
    full_name     TEXT NOT NULL,
    country       TEXT NOT NULL,
    team_id       INTEGER REFERENCES teams(team_id),
    playing_role  TEXT,
    batting_style TEXT,
    bowling_style TEXT,
    date_of_birth DATE
);

CREATE TABLE venues (
    venue_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    cb_venue_id INTEGER UNIQUE,
    venue_name  TEXT NOT NULL,
    city        TEXT,
    country     TEXT,
    capacity    INTEGER CHECK (capacity IS NULL OR capacity > 0)
);

CREATE TABLE series (
    series_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    cb_series_id   INTEGER UNIQUE,
    series_name    TEXT NOT NULL,
    host_country   TEXT,
    match_type     TEXT,
    start_date     DATE,
    end_date       DATE,
    total_matches  INTEGER CHECK (total_matches IS NULL OR total_matches >= 0)
);

CREATE TABLE matches (
    match_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    cb_match_id     INTEGER UNIQUE,
    series_id       INTEGER REFERENCES series(series_id),
    description     TEXT,
    match_format    TEXT NOT NULL CHECK (match_format IN ('Test','ODI','T20I')),
    team1_id        INTEGER NOT NULL REFERENCES teams(team_id),
    team2_id        INTEGER NOT NULL REFERENCES teams(team_id),
    venue_id        INTEGER REFERENCES venues(venue_id),
    match_date      DATE NOT NULL,
    status          TEXT,
    toss_winner_id  INTEGER REFERENCES teams(team_id),
    toss_decision   TEXT CHECK (toss_decision IN ('bat','bowl')),
    winner_id       INTEGER REFERENCES teams(team_id),
    victory_margin  INTEGER,
    victory_type    TEXT CHECK (victory_type IN ('runs','wickets','draw','tie')),
    match_type      TEXT,
    CHECK (team1_id <> team2_id)
);

CREATE TABLE innings (
    innings_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        INTEGER NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    innings_no      INTEGER NOT NULL CHECK (innings_no BETWEEN 1 AND 4),
    batting_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    total_runs      INTEGER CHECK (total_runs >= 0),
    wickets         INTEGER CHECK (wickets BETWEEN 0 AND 10),
    overs           REAL,
    UNIQUE (match_id, innings_no)
);

CREATE TABLE batting_scorecard (
    bat_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    innings_id       INTEGER NOT NULL REFERENCES innings(innings_id) ON DELETE CASCADE,
    player_id        INTEGER NOT NULL REFERENCES players(player_id),
    batting_position INTEGER CHECK (batting_position BETWEEN 1 AND 11),
    runs             INTEGER NOT NULL DEFAULT 0 CHECK (runs >= 0),
    balls            INTEGER NOT NULL DEFAULT 0 CHECK (balls >= 0),
    fours            INTEGER DEFAULT 0,
    sixes            INTEGER DEFAULT 0,
    strike_rate      REAL,
    is_out           INTEGER NOT NULL DEFAULT 1 CHECK (is_out IN (0,1)),
    UNIQUE (innings_id, player_id)
);

CREATE TABLE bowling_scorecard (
    bowl_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    innings_id     INTEGER NOT NULL REFERENCES innings(innings_id) ON DELETE CASCADE,
    player_id      INTEGER NOT NULL REFERENCES players(player_id),
    overs          REAL NOT NULL CHECK (overs >= 0),
    maidens        INTEGER DEFAULT 0,
    runs_conceded  INTEGER NOT NULL CHECK (runs_conceded >= 0),
    wickets        INTEGER NOT NULL DEFAULT 0 CHECK (wickets BETWEEN 0 AND 10),
    economy        REAL,
    UNIQUE (innings_id, player_id)
);

CREATE TABLE fielding_stats (
    field_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id   INTEGER NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    player_id  INTEGER NOT NULL REFERENCES players(player_id),
    catches    INTEGER NOT NULL DEFAULT 0 CHECK (catches >= 0),
    stumpings  INTEGER NOT NULL DEFAULT 0 CHECK (stumpings >= 0),
    UNIQUE (match_id, player_id)
);

CREATE TABLE player_career_stats (
    stat_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id      INTEGER NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    format         TEXT NOT NULL CHECK (format IN ('Test','ODI','T20I')),
    matches_played INTEGER DEFAULT 0,
    runs           INTEGER DEFAULT 0,
    highest_score  INTEGER DEFAULT 0,
    batting_avg    REAL,
    strike_rate    REAL,
    centuries      INTEGER DEFAULT 0,
    wickets        INTEGER DEFAULT 0,
    bowling_avg    REAL,
    economy        REAL,
    UNIQUE (player_id, format)
);

-- Indexes
CREATE INDEX idx_matches_date    ON matches(match_date);
CREATE INDEX idx_matches_venue   ON matches(venue_id);
CREATE INDEX idx_players_country ON players(country);
CREATE INDEX idx_venues_capacity ON venues(capacity);
CREATE INDEX idx_bat_player      ON batting_scorecard(player_id);
CREATE INDEX idx_bowl_player     ON bowling_scorecard(player_id);
CREATE INDEX idx_innings_match   ON innings(match_id);