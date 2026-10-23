"""SQL access for the players table. No business rules here."""
import sqlite3
from typing import Optional

from database.connection import get_connection
from models.player import Player

UPDATABLE = {"full_name", "country", "playing_role", "batting_style",
             "bowling_style", "date_of_birth", "team_id"}


def _row_to_player(row: sqlite3.Row) -> Player:
    return Player(
        player_id=row["player_id"], full_name=row["full_name"],
        country=row["country"], playing_role=row["playing_role"],
        batting_style=row["batting_style"], bowling_style=row["bowling_style"],
        date_of_birth=row["date_of_birth"], team_id=row["team_id"],
    )


def insert(p: Player) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO players (full_name, country, team_id, playing_role,
                                    batting_style, bowling_style, date_of_birth)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (p.full_name, p.country, p.team_id, p.playing_role,
             p.batting_style, p.bowling_style, p.date_of_birth),
        )
        return cur.lastrowid


def get_by_id(player_id: int) -> Optional[Player]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM players WHERE player_id = ?",
                           (player_id,)).fetchone()
    return _row_to_player(row) if row else None


def find_duplicate(full_name: str, country: str,
                   exclude_id: int | None = None) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            """SELECT 1 FROM players
               WHERE LOWER(full_name) = LOWER(?) AND LOWER(country) = LOWER(?)
                 AND player_id <> COALESCE(?, -1) LIMIT 1""",
            (full_name, country, exclude_id),
        ).fetchone()
    return row is not None


def list_players(search: str = "", country: str = "",
                 limit: int = 50, offset: int = 0) -> list[Player]:
    sql = "SELECT * FROM players WHERE 1=1"
    params: list = []
    if search:
        sql += " AND full_name LIKE ?"
        params.append(f"%{search}%")
    if country:
        sql += " AND country = ?"
        params.append(country)
    sql += " ORDER BY full_name LIMIT ? OFFSET ?"
    params += [limit, offset]
    with get_connection() as conn:
        return [_row_to_player(r) for r in conn.execute(sql, params)]


def update(player_id: int, fields: dict) -> int:
    """Update whitelisted columns only. Returns rows changed."""
    cols = [c for c in fields if c in UPDATABLE]
    if not cols:
        return 0
    set_clause = ", ".join(f"{c} = ?" for c in cols)  # names are whitelisted
    values = [fields[c] for c in cols] + [player_id]
    with get_connection() as conn:
        cur = conn.execute(
            f"UPDATE players SET {set_clause} WHERE player_id = ?", values)
        return cur.rowcount


def is_referenced(player_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            """SELECT 1 WHERE EXISTS (SELECT 1 FROM batting_scorecard WHERE player_id = ?)
                  OR EXISTS (SELECT 1 FROM bowling_scorecard WHERE player_id = ?)
                  OR EXISTS (SELECT 1 FROM fielding_stats WHERE player_id = ?)""",
            (player_id, player_id, player_id),
        ).fetchone()
    return row is not None


def delete(player_id: int) -> int:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM players WHERE player_id = ?",
                           (player_id,))
        return cur.rowcount