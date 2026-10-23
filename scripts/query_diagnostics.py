"""Explain why a SQL question returns no rows.

For each data-hungry question it shows the threshold the question asks for
and the best value your data actually reaches. Read-only; no API calls.

  python scripts/query_diagnostics.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_readonly_connection  # noqa: E402

OVERVIEW = {
    "real matches": "SELECT COUNT(*) FROM matches WHERE cb_match_id IS NOT NULL",
    "earliest match": "SELECT MIN(match_date) FROM matches WHERE cb_match_id IS NOT NULL",
    "latest match": "SELECT MAX(match_date) FROM matches WHERE cb_match_id IS NOT NULL",
    "matches with a venue": "SELECT COUNT(*) FROM matches WHERE venue_id IS NOT NULL",
    "innings": "SELECT COUNT(*) FROM innings",
    "batting rows": "SELECT COUNT(*) FROM batting_scorecard",
    "bowling rows": "SELECT COUNT(*) FROM bowling_scorecard",
    "players with career stats": "SELECT COUNT(DISTINCT player_id) FROM player_career_stats",
    "series": "SELECT COUNT(*) FROM series",
}

# (question, what the spec requires, SQL returning the best value in the data)
CHECKS = [
    ("Q9  runs>1000 and wickets>50 in one format", "2 conditions",
     """SELECT COUNT(*) FROM player_career_stats
        WHERE runs > 1000 AND wickets > 50"""),
    ("Q14 matches by one bowler at one venue (>=4 overs)", 3,
     """SELECT COALESCE(MAX(c), 0) FROM (
          SELECT COUNT(DISTINCT m.match_id) c FROM bowling_scorecard bs
          JOIN innings i ON i.innings_id = bs.innings_id
          JOIN matches m ON m.match_id = i.match_id
          JOIN venues v ON v.venue_id = m.venue_id
          WHERE bs.overs >= 4 GROUP BY bs.player_id, v.venue_id)"""),
    ("Q16 matches by one batter in one year (since 2020)", 5,
     """SELECT COALESCE(MAX(c), 0) FROM (
          SELECT COUNT(DISTINCT m.match_id) c FROM batting_scorecard b
          JOIN innings i ON i.innings_id = b.innings_id
          JOIN matches m ON m.match_id = i.match_id
          WHERE m.match_date >= '2020-01-01'
          GROUP BY b.player_id, strftime('%Y', m.match_date))"""),
    ("Q18 ODI/T20I matches bowled by one bowler", 10,
     """SELECT COALESCE(MAX(c), 0) FROM (
          SELECT COUNT(DISTINCT m.match_id) c FROM bowling_scorecard bs
          JOIN innings i ON i.innings_id = bs.innings_id
          JOIN matches m ON m.match_id = i.match_id
          WHERE m.match_format IN ('ODI', 'T20I') GROUP BY bs.player_id)"""),
    ("Q22 matches between one team pair (last 3 years)", 5,
     """SELECT COALESCE(MAX(c), 0) FROM (
          SELECT COUNT(*) c FROM matches
          WHERE match_date >= date('now', '-3 years')
          GROUP BY MIN(team1_id, team2_id), MAX(team1_id, team2_id))"""),
    ("Q23 batting innings recorded for one player", 5,
     """SELECT COALESCE(MAX(c), 0) FROM (
          SELECT COUNT(*) c FROM batting_scorecard GROUP BY player_id)"""),
    ("Q24 times one batting pair appears together", 5,
     """SELECT COALESCE(MAX(c), 0) FROM (
          SELECT COUNT(*) c FROM batting_scorecard b1
          JOIN batting_scorecard b2 ON b2.innings_id = b1.innings_id
           AND b2.batting_position = b1.batting_position + 1
          GROUP BY MIN(b1.player_id, b2.player_id),
                   MAX(b1.player_id, b2.player_id))"""),
    ("Q25 quarters with >=3 matches for one batter", 6,
     """SELECT COALESCE(MAX(n), 0) FROM (
          SELECT COUNT(*) n FROM (
            SELECT b.player_id,
                   strftime('%Y', m.match_date) || '-Q' ||
                   ((CAST(strftime('%m', m.match_date) AS INTEGER) + 2) / 3) q
            FROM batting_scorecard b
            JOIN innings i ON i.innings_id = b.innings_id
            JOIN matches m ON m.match_id = i.match_id
            GROUP BY b.player_id, q HAVING COUNT(DISTINCT m.match_id) >= 3)
          GROUP BY player_id)"""),
    ("Q25 quarters with >=1 match for one batter", "-",
     """SELECT COALESCE(MAX(n), 0) FROM (
          SELECT COUNT(DISTINCT strftime('%Y', m.match_date) || '-Q' ||
                   ((CAST(strftime('%m', m.match_date) AS INTEGER) + 2) / 3)) n
          FROM batting_scorecard b
          JOIN innings i ON i.innings_id = b.innings_id
          JOIN matches m ON m.match_id = i.match_id
          GROUP BY b.player_id)"""),
]


def main():
    with get_readonly_connection() as conn:
        print("DATA OVERVIEW")
        for label, sql in OVERVIEW.items():
            print(f"  {label:28} {conn.execute(sql).fetchone()[0]}")
        print("\nTHRESHOLDS: spec asks vs best your data reaches")
        for label, spec, sql in CHECKS:
            best = conn.execute(sql).fetchone()[0]
            verdict = ""
            if isinstance(spec, int):
                verdict = "OK" if best >= spec else "TOO LITTLE DATA"
            print(f"  {label:52} spec={spec!s:12} data={best!s:6} {verdict}")


if __name__ == "__main__":
    main()