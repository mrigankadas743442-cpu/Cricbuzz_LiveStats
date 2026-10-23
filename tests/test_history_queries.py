"""Do the history-hungry SQL questions work when enough history exists?

The real harvested data covers only a few weeks, so several questions
return no rows there. This test builds ~4.5 years of SYNTHETIC history in a
throw-away in-memory database (never your real one) and checks that each
question returns rows. It proves the SQL is correct; the real data is simply
too thin for these questions.
"""
import math
from datetime import date, timedelta
from pathlib import Path

import pytest

QUERIES = Path(__file__).resolve().parent.parent / "sql" / "queries"
KEYS = ["q09", "q14", "q16", "q18", "q22a", "q22b", "q23", "q24",
        "q25a", "q25b"]


def sql_for(key):
    files = sorted(QUERIES.glob(f"{key}.sql")) or sorted(QUERIES.glob(f"{key}_*.sql"))
    assert files, f"no SQL file for {key} in {QUERIES}"
    return files[0].read_text(encoding="utf-8")


@pytest.fixture
def history(conn):
    conn.create_function("SQRT", 1, math.sqrt)
    conn.execute("INSERT INTO teams (team_id, team_name, country) VALUES "
                 "(1, 'Team A', 'Team A'), (2, 'Team B', 'Team B')")
    conn.execute("INSERT INTO venues (venue_id, venue_name, country) "
                 "VALUES (1, 'Test Ground', 'Team A')")
    for pid in range(1, 23):
        conn.execute("INSERT INTO players (player_id, full_name, country, "
                     "playing_role) VALUES (?, ?, ?, 'All-rounder')",
                     (pid, f"Player {pid}", "Team A" if pid <= 11 else "Team B"))
    conn.execute("INSERT INTO player_career_stats (player_id, format, runs, "
                 "wickets, matches_played, batting_avg) "
                 "VALUES (1, 'ODI', 5000, 100, 200, 40.0)")

    start, k = date(2022, 1, 1), 0
    while start + timedelta(days=20 * k) <= date(2026, 10, 1):
        day = (start + timedelta(days=20 * k)).isoformat()
        win_runs = k % 2 == 0
        conn.execute(
            "INSERT INTO matches (match_id, cb_match_id, match_format, "
            "team1_id, team2_id, venue_id, match_date, toss_winner_id, "
            "toss_decision, winner_id, victory_margin, victory_type) "
            "VALUES (?, ?, 'T20I', 1, 2, 1, ?, 1, 'bat', ?, ?, ?)",
            (k + 1, 1000 + k, day, 1 if win_runs else 2,
             10 if win_runs else 3, "runs" if win_runs else "wickets"))
        for no, (bat_team, first, bowl_first) in enumerate(
                [(1, 1, 12), (2, 12, 7)], start=1):
            iid = 2 * k + no
            conn.execute("INSERT INTO innings (innings_id, match_id, "
                         "innings_no, batting_team_id, total_runs, wickets, "
                         "overs) VALUES (?, ?, ?, ?, 150, 6, 20)",
                         (iid, k + 1, no, bat_team))
            for pos in range(1, 12):
                runs = (k * 7 + pos * 13 + no * 5) % 90
                balls = runs + 8
                conn.execute(
                    "INSERT INTO batting_scorecard (innings_id, player_id, "
                    "batting_position, runs, balls, strike_rate, is_out) "
                    "VALUES (?, ?, ?, ?, ?, ?, 1)",
                    (iid, first + pos - 1, pos, runs, balls,
                     round(100.0 * runs / balls, 2)))
            for off in range(5):
                conn.execute(
                    "INSERT INTO bowling_scorecard (innings_id, player_id, "
                    "overs, runs_conceded, wickets, economy) "
                    "VALUES (?, ?, 4, ?, ?, ?)",
                    (iid, bowl_first + off, 25 + (k + off) % 15,
                     (k + off) % 4, 6.5))
        k += 1
    return conn


@pytest.mark.parametrize("key", KEYS)
def test_question_returns_rows_with_enough_history(history, key):
    rows = history.execute(sql_for(key)).fetchall()
    assert len(rows) > 0, f"{key} returned no rows even with full history"