"""Explain why a cached scorecard did not load (reads local data only)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_connection

with get_connection() as conn:
    print("matches rows:", conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0])
    print("teams rows:  ", conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0])
    rows = conn.execute(
        "SELECT path, body FROM api_cache WHERE path LIKE '/mcenter/v1/%/scard'"
    ).fetchall()
    for row in rows:
        mid = int(row["path"].split("/")[3])
        payload = json.loads(row["body"])
        match = conn.execute(
            "SELECT match_id, team1_id, team2_id FROM matches WHERE cb_match_id = ?",
            (mid,)).fetchone()
        print(f"\nmatch {mid}: in matches table? {'yes' if match else 'NO'}")
        if match:
            names = [r["team_name"] for r in conn.execute(
                "SELECT team_name FROM teams WHERE team_id IN (?, ?)",
                (match["team1_id"], match["team2_id"]))]
            print("  team names in DB:     ", names)
        print("  batteamname in payload:",
              [i.get("batteamname") for i in payload.get("scorecard") or []])