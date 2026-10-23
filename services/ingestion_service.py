"""Parse Cricbuzz match lists and upsert into SQL."""
import sqlite3
from datetime import datetime, timezone

from database.connection import get_connection
from utils.logger import get_logger

log = get_logger(__name__)

FORMAT_MAP = {"TEST": "Test", "ODI": "ODI", "T20": "T20I", "T20I": "T20I"}


def iter_match_infos(payload: dict):
    """Yield (matchInfo, category) from a /matches/v1/* response.

    category is the block's matchType: 'International', 'League',
    'Domestic' or 'Women'.
    """
    for type_block in payload.get("typeMatches", []):
        category = type_block.get("matchType")
        for series in type_block.get("seriesMatches", []):
            wrapper = series.get("seriesAdWrapper")
            if not wrapper:
                continue
            for m in wrapper.get("matches", []):
                info = m.get("matchInfo")
                if info:
                    yield info, category


def _upsert_team(conn, team: dict) -> int:
    """Find a team by Cricbuzz ID, then by name, else create it."""
    cb_id, name = team["teamId"], team["teamName"]
    row = conn.execute("SELECT team_id FROM teams WHERE cb_team_id = ?",
                       (cb_id,)).fetchone()
    if row:
        return row[0]
    row = conn.execute("SELECT team_id FROM teams WHERE team_name = ?",
                       (name,)).fetchone()
    if row:  # e.g. a seed team: adopt it and attach the Cricbuzz ID
        conn.execute("UPDATE teams SET cb_team_id = ? WHERE team_id = ?",
                     (cb_id, row[0]))
        return row[0]
    cur = conn.execute(
        "INSERT INTO teams (cb_team_id, team_name, short_name, country) "
        "VALUES (?, ?, ?, ?)", (cb_id, name, team.get("teamSName"), name))
    return cur.lastrowid


def _upsert_venue(conn, venue: dict | None) -> int | None:
    if not venue or "id" not in venue:
        return None
    conn.execute(
        """INSERT INTO venues (cb_venue_id, venue_name, city)
           VALUES (?, ?, ?)
           ON CONFLICT(cb_venue_id) DO UPDATE SET venue_name = excluded.venue_name""",
        (venue["id"], venue.get("ground", "Unknown"), venue.get("city")))
    return conn.execute("SELECT venue_id FROM venues WHERE cb_venue_id = ?",
                        (venue["id"],)).fetchone()[0]


def _ms_to_date(value) -> str | None:
    """Cricbuzz timestamps are epoch milliseconds, often sent as strings."""
    try:
        return datetime.fromtimestamp(
            int(value) / 1000, tz=timezone.utc).date().isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _upsert_series(conn, info: dict, fmt: str) -> int | None:
    """Save the series a match belongs to. Returns its series_id."""
    cb_id, name = info.get("seriesId"), info.get("seriesName")
    if not cb_id or not name:
        return None
    conn.execute(
        """INSERT INTO series (cb_series_id, series_name, match_type,
                               start_date, end_date)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(cb_series_id) DO UPDATE SET
               series_name = excluded.series_name,
               start_date  = COALESCE(excluded.start_date, series.start_date),
               end_date    = COALESCE(excluded.end_date, series.end_date)""",
        (cb_id, name, fmt, _ms_to_date(info.get("seriesStartDt")),
         _ms_to_date(info.get("seriesEndDt"))))
    return conn.execute("SELECT series_id FROM series WHERE cb_series_id = ?",
                        (cb_id,)).fetchone()[0]


def ingest_matches(payload: dict) -> int:
    """Save matches from an API payload. Returns number saved.

    Skipped matches are counted by reason and logged, never hidden.
    """
    saved = 0
    skipped: dict[str, int] = {}
    with get_connection() as conn:
        for info, category in iter_match_infos(payload):
            fmt = FORMAT_MAP.get(str(info.get("matchFormat", "")).upper())
            if fmt is None:
                skipped["unsupported format"] = skipped.get("unsupported format", 0) + 1
                continue
            try:
                t1 = _upsert_team(conn, info["team1"])
                t2 = _upsert_team(conn, info["team2"])
                venue_id = _upsert_venue(conn, info.get("venueInfo"))
                series_id = _upsert_series(conn, info, fmt)
                date = datetime.fromtimestamp(
                    int(info["startDate"]) / 1000, tz=timezone.utc
                ).date().isoformat()
                conn.execute(
                    """INSERT INTO matches
                           (cb_match_id, series_id, description, match_format,
                            team1_id, team2_id, venue_id, match_date, status,
                            match_type)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(cb_match_id) DO UPDATE SET
                           status = excluded.status,
                           match_type = excluded.match_type,
                           series_id = COALESCE(excluded.series_id,
                                                matches.series_id)""",
                    (info["matchId"], series_id, info.get("matchDesc"), fmt,
                     t1, t2, venue_id, date, info.get("status"), category))
                saved += 1
            except (KeyError, ValueError, TypeError, sqlite3.Error) as exc:
                key = f"{type(exc).__name__}: {exc}"
                skipped[key] = skipped.get(key, 0) + 1
        # How many of each series' matches we hold (not the series' full size).
        conn.execute(
            """UPDATE series SET total_matches =
                   (SELECT COUNT(*) FROM matches
                    WHERE matches.series_id = series.series_id)
               WHERE series_id IN (SELECT series_id FROM matches)""")
    for reason, n in skipped.items():
        log.warning("Skipped %d matches: %s", n, reason)
    return saved