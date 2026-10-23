"""Data for the Home page."""
import sqlite3

import config
from database.connection import get_connection
from utils.logger import get_logger

log = get_logger(__name__)

# Fixed whitelist: table names can't be bound as parameters.
_TABLES = {
    "Players": "players",
    "Matches": "matches",
    "Venues": "venues",
    "Series": "series",
}


def get_home_stats() -> dict[str, int]:
    """Return row counts for key tables.

    Raises:
        sqlite3.Error: if the database is missing or unreadable.
    """
    stats: dict[str, int] = {}
    with get_connection() as conn:
        for label, table in _TABLES.items():
            stats[label] = conn.execute(
                f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return stats


def api_key_configured() -> bool:
    return bool(config.RAPIDAPI_KEY)