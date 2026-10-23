"""Store raw API responses in their own SQLite file (data/api_cache.db).

Kept separate from cricket.db so rebuilding the main database with
init_db.py can never delete the cached API data.
"""
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlencode

CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "api_cache.db"

_DDL = """
CREATE TABLE IF NOT EXISTS api_cache (
    cache_key  TEXT PRIMARY KEY,
    path       TEXT NOT NULL,
    body       TEXT NOT NULL,
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)"""


def _key(path: str, params: dict | None) -> str:
    return path + ("?" + urlencode(sorted(params.items())) if params else "")


def _connect() -> sqlite3.Connection:
    CACHE_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(CACHE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(_DDL)
    return conn


def get(path: str, params: dict | None = None,
        max_age_hours: int | None = None):
    """Return the saved JSON (as a dict), or None if missing/too old."""
    sql = "SELECT body FROM api_cache WHERE cache_key = ?"
    args: list = [_key(path, params)]
    if max_age_hours is not None:
        sql += " AND fetched_at >= datetime('now', ?)"
        args.append(f"-{max_age_hours} hours")
    conn = _connect()
    try:
        row = conn.execute(sql, args).fetchone()
    finally:
        conn.close()
    return json.loads(row["body"]) if row else None


def put(path: str, params: dict | None, data: dict) -> None:
    conn = _connect()
    try:
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO api_cache (cache_key, path, body) "
                "VALUES (?, ?, ?)", (_key(path, params), path, json.dumps(data)))
    finally:
        conn.close()


def items(path_like: str) -> list[tuple[str, dict]]:
    """All cached (path, payload) pairs whose path matches a SQL LIKE."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT path, body FROM api_cache WHERE path LIKE ?",
            (path_like,)).fetchall()
    finally:
        conn.close()
    return [(r["path"], json.loads(r["body"])) for r in rows]


def import_rows(rows) -> None:
    """Copy (cache_key, path, body, fetched_at) rows in; existing ones stay."""
    conn = _connect()
    try:
        with conn:
            conn.executemany(
                "INSERT OR IGNORE INTO api_cache "
                "(cache_key, path, body, fetched_at) VALUES (?, ?, ?, ?)", rows)
    finally:
        conn.close()