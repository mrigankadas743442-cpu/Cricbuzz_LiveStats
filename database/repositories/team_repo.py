"""SQL access for the teams table."""
from database.connection import get_connection


def list_teams() -> list[tuple[int, str]]:
    """Return (team_id, team_name) pairs, alphabetical."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT team_id, team_name FROM teams ORDER BY team_name"
        ).fetchall()
    return [(r["team_id"], r["team_name"]) for r in rows]