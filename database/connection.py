
"""SQLite connection management."""
import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote

# Resolve the database path independently of the working directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "cricket.db"


def _prepare(conn: sqlite3.Connection) -> sqlite3.Connection:
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.create_function(
        "SQRT",
        1,
        lambda x: None if x is None else math.sqrt(x),
    )
    return conn


@contextmanager
def get_connection(db_path: Path = DB_PATH):
    """Yield a connection; commit on success, roll back on error."""
    db_path = Path(db_path).resolve()

    # Ensure the parent directory exists before opening SQLite.
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = _prepare(sqlite3.connect(str(db_path)))
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_readonly_connection(db_path: Path = DB_PATH):
    """Connection that physically cannot write (used for custom SQL)."""
    db_path = Path(db_path).resolve()

    if not db_path.is_file():
        raise FileNotFoundError(
            f"Database file not found: {db_path}"
        )

    # Properly encode the absolute path for SQLite URI mode.
    db_uri = f"{quote(str(db_path), safe='/')}?mode=ro"
    conn = _prepare(
        sqlite3.connect(f"file:{db_uri}", uri=True)
    )
    conn.execute("PRAGMA query_only = ON")

    try:
        yield conn
    finally:
        conn.close()
