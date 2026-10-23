from contextlib import contextmanager

import pytest

from services import ingestion_service

INFO = {"matchId": 5001, "matchDesc": "2nd T20I", "matchFormat": "T20",
        "startDate": "1760400000000", "status": "India won by 5 wkts",
        "team1": {"teamId": 2, "teamName": "India", "teamSName": "IND"},
        "team2": {"teamId": 10, "teamName": "West Indies", "teamSName": "WI"},
        "venueInfo": {"id": 77, "ground": "Eden Gardens", "city": "Kolkata"}}


def payload(*infos, category="International"):
    return {"typeMatches": [{"matchType": category, "seriesMatches": [
        {"seriesAdWrapper": {"matches": [{"matchInfo": i} for i in infos]}}]}]}


@pytest.fixture(autouse=True)
def use_test_db(conn, monkeypatch):
    """Point the service at the in-memory test database."""
    @contextmanager
    def fake_connection():
        yield conn
    monkeypatch.setattr(ingestion_service, "get_connection", fake_connection)


def count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_saves_match_teams_and_venue(conn):
    assert ingestion_service.ingest_matches(payload(INFO)) == 1
    assert count(conn, "matches") == 1
    assert count(conn, "teams") == 2
    assert count(conn, "venues") == 1


def test_stores_category_as_match_type(conn):
    ingestion_service.ingest_matches(payload(INFO, category="Women"))
    row = conn.execute("SELECT match_type FROM matches").fetchone()
    assert row[0] == "Women"


def test_running_twice_does_not_duplicate(conn):
    ingestion_service.ingest_matches(payload(INFO))
    ingestion_service.ingest_matches(payload(INFO))
    assert count(conn, "matches") == 1
    assert count(conn, "teams") == 2


def test_unsupported_format_is_skipped(conn):
    other = dict(INFO, matchId=5002, matchFormat="T10")
    assert ingestion_service.ingest_matches(payload(other)) == 0
    assert count(conn, "matches") == 0


def test_existing_seed_team_is_adopted_not_duplicated(conn):
    conn.execute("INSERT INTO teams (team_name, country) "
                 "VALUES ('India', 'India')")
    ingestion_service.ingest_matches(payload(INFO))
    assert count(conn, "teams") == 2
    cb = conn.execute("SELECT cb_team_id FROM teams "
                      "WHERE team_name = 'India'").fetchone()[0]
    assert cb == 2

def test_series_is_saved_and_linked(conn):
    info = dict(INFO, seriesId=777, seriesName="India tour of West Indies",
                seriesStartDt="1760000000000", seriesEndDt="1761000000000")
    ingestion_service.ingest_matches(payload(info))
    s = conn.execute("SELECT series_name, start_date, end_date, total_matches "
                     "FROM series").fetchone()
    assert s[0] == "India tour of West Indies"
    assert s[1] == "2025-10-09" and s[2] == "2025-10-20"
    assert s[3] == 1
    linked = conn.execute("SELECT s.cb_series_id FROM matches m "
                          "JOIN series s ON s.series_id = m.series_id").fetchone()
    assert linked[0] == 777


def test_match_without_series_is_still_saved(conn):
    assert ingestion_service.ingest_matches(payload(INFO)) == 1
    assert conn.execute("SELECT COUNT(*) FROM series").fetchone()[0] == 0