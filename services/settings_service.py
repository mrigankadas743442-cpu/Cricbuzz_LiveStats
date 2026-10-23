"""Operations used by the Settings page."""
import os
from pathlib import Path

import config
from api.cricbuzz_client import CricbuzzClient
from database.connection import DB_PATH, get_connection
from services.ingestion_service import ingest_matches

# Fixed whitelist: table names can't be bound as parameters.
TABLES = [
    "teams", "players", "venues", "series", "matches", "innings",
    "batting_scorecard", "bowling_scorecard", "fielding_stats",
    "player_career_stats",
]


def api_key_configured() -> bool:
    return bool(config.RAPIDAPI_KEY)


def test_api() -> int:
    """Make one real call. Returns the number of matches in the response.

    Raises CricbuzzAPIError on failure (bad key, network, quota).
    """
    from services.match_service import parse_matches
    payload = CricbuzzClient().recent_matches()
    return len(parse_matches(payload))


def refresh_recent_matches() -> int:
    """Fetch recent matches and save them. Returns number processed."""
    return ingest_matches(CricbuzzClient().recent_matches())


def database_info() -> dict:
    """File path, size in KB and row count per table."""
    path = Path(DB_PATH)
    size_kb = round(os.path.getsize(path) / 1024, 1) if path.exists() else 0
    counts: dict[str, int] = {}
    with get_connection() as conn:
        for table in TABLES:
            counts[table] = conn.execute(
                f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return {"path": str(path), "size_kb": size_kb, "counts": counts}