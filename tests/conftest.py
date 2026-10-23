"""Shared fixtures. Every test gets a fresh in-memory database."""
import sqlite3
from pathlib import Path

import pytest

SCHEMA = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


@pytest.fixture
def conn():
    """Empty database built from sql/schema.sql (never touches data/)."""
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    c.executescript(SCHEMA.read_text(encoding="utf-8"))
    yield c
    c.close()


@pytest.fixture
def two_teams(conn):
    """India (id 1) and West Indies (id 2) plus one T20I between them."""
    conn.execute("INSERT INTO teams (team_id, cb_team_id, team_name, country) "
                 "VALUES (1, 2, 'India', 'India'), "
                 "(2, 10, 'West Indies', 'West Indies')")
    conn.execute("INSERT INTO matches (match_id, cb_match_id, match_format, "
                 "team1_id, team2_id, match_date) "
                 "VALUES (1, 151602, 'T20I', 1, 2, '2026-10-14')")
    return conn