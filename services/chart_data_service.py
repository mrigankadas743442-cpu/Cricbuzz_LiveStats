"""SQL for the Charts page. Real players only (seed 'Sample Player' rows
and seed matches are excluded)."""
import pandas as pd

from database.connection import get_readonly_connection

REAL = "p.full_name NOT LIKE 'Sample Player%'"


def _query(sql: str, params: tuple = ()) -> pd.DataFrame:
    with get_readonly_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def top_scorers(fmt: str = "All", limit: int = 10) -> pd.DataFrame:
    return _query(
        f"""SELECT p.full_name AS player, SUM(b.runs) AS runs
            FROM batting_scorecard b
            JOIN players p ON p.player_id = b.player_id
            JOIN innings i ON i.innings_id = b.innings_id
            JOIN matches m ON m.match_id = i.match_id
            WHERE {REAL} AND (? = 'All' OR m.match_format = ?)
            GROUP BY p.player_id
            ORDER BY runs DESC
            LIMIT ?""", (fmt, fmt, limit))


def batters() -> pd.DataFrame:
    return _query(
        f"""SELECT p.player_id, p.full_name AS player
            FROM players p
            WHERE {REAL}
              AND p.player_id IN (SELECT player_id FROM batting_scorecard)
            ORDER BY p.full_name""")


def player_form(player_id: int) -> pd.DataFrame:
    return _query(
        """SELECT m.match_date AS date, b.runs,
                  m.match_format || ' · ' || COALESCE(m.description, '')
                      AS match
           FROM batting_scorecard b
           JOIN innings i ON i.innings_id = b.innings_id
           JOIN matches m ON m.match_id = i.match_id
           WHERE b.player_id = ?
           ORDER BY m.match_date, i.innings_no""", (player_id,))


def wins_by_team() -> pd.DataFrame:
    return _query(
        """SELECT t.team_name AS team, COUNT(*) AS wins
           FROM matches m
           JOIN teams t ON t.team_id = m.winner_id
           WHERE m.cb_match_id IS NOT NULL
           GROUP BY t.team_id
           ORDER BY wins DESC""")


def average_vs_strike_rate(min_balls: int = 30) -> pd.DataFrame:
    df = _query(
        f"""SELECT p.full_name AS player,
                   SUM(b.runs) AS runs,
                   ROUND(100.0 * SUM(b.runs) / SUM(b.balls), 1)
                       AS strike_rate,
                   ROUND(1.0 * SUM(b.runs) / NULLIF(SUM(b.is_out), 0), 1)
                       AS average
            FROM batting_scorecard b
            JOIN players p ON p.player_id = b.player_id
            WHERE {REAL}
            GROUP BY p.player_id
            HAVING SUM(b.balls) >= ?""", (min_balls,))
    return df.dropna(subset=["average", "strike_rate"])   # never dismissed