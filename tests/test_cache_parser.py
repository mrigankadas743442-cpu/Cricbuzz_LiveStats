from services.cache_parser import parse_scorecard

PAYLOAD = {"scorecard": [{
    "inningsid": 1, "batteamname": "India", "score": 118, "wickets": 5,
    "overs": 7.4,
    "batsman": [
        {"id": 8271, "name": "Sanju Samson", "runs": 16, "balls": 7,
         "fours": 2, "sixes": 1, "strkrate": "228.57",
         "outdec": "b Shamar Springer"},
        {"id": 99, "name": "Not Out Guy", "runs": 40, "balls": 20,
         "fours": 4, "sixes": 2, "strkrate": "200.00", "outdec": "not out"},
        {"id": 100, "name": "Did Not Bat", "runs": 0, "balls": 0,
         "outdec": ""},
    ],
    "bowler": [{"id": 11214, "name": "Keemo Paul", "overs": "2",
                "maidens": 0, "wickets": 2, "runs": 34, "economy": "17"}],
}]}


def count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_saves_innings_batting_and_bowling(two_teams):
    assert parse_scorecard(two_teams, 151602, PAYLOAD) == 1
    assert count(two_teams, "innings") == 1
    assert count(two_teams, "bowling_scorecard") == 1


def test_did_not_bat_rows_are_skipped(two_teams):
    parse_scorecard(two_teams, 151602, PAYLOAD)
    assert count(two_teams, "batting_scorecard") == 2


def test_not_out_batter_is_marked_not_out(two_teams):
    parse_scorecard(two_teams, 151602, PAYLOAD)
    rows = dict(two_teams.execute(
        "SELECT p.full_name, b.is_out FROM batting_scorecard b "
        "JOIN players p ON p.player_id = b.player_id").fetchall())
    assert rows["Sanju Samson"] == 1
    assert rows["Not Out Guy"] == 0


def test_running_twice_does_not_duplicate(two_teams):
    parse_scorecard(two_teams, 151602, PAYLOAD)
    parse_scorecard(two_teams, 151602, PAYLOAD)
    assert count(two_teams, "innings") == 1
    assert count(two_teams, "batting_scorecard") == 2
    assert count(two_teams, "players") == 3


def test_unknown_match_saves_nothing(two_teams):
    assert parse_scorecard(two_teams, 999999, PAYLOAD) == 0
    assert count(two_teams, "innings") == 0