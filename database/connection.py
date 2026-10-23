"""SQLite connection management."""
import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cricket.db"


def _prepare(conn: sqlite3.Connection) -> sqlite3.Connection:
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.create_function("SQRT", 1, lambda x: None if x is None else math.sqrt(x))
    return conn


@contextmanager
def get_connection(db_path: Path = DB_PATH):
    """Yield a connection; commit on success, roll back on error."""
    conn = _prepare(sqlite3.connect(db_path))
    try:
        yield conn
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_readonly_connection(db_path: Path = DB_PATH):
    """Connection that physically cannot write (used for custom SQL)."""
    conn = _prepare(sqlite3.connect(f"file:{db_path}?mode=ro", uri=True))
    conn.execute("PRAGMA query_only = ON")
    try:
        yield conn
    finally:
        conn.close()