"""Look up stadium capacity (and country) for venues that lack it.

Capacity comes with a match's detail response (/mcenter/v1/{match_id}), so
we fetch ONE match per venue, biggest and most international venues first.
Each response is cached, so nothing is ever fetched twice. Also fills the
venue country (used by Q12 home/away) and the toss for that match.

  python scripts/harvest_venues.py --max-calls 30
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.cricbuzz_client import CricbuzzAPIError, CricbuzzClient  # noqa: E402
from database.connection import get_connection                    # noqa: E402
from services import raw_store                                      # noqa: E402
from services.match_info_parser import parse_match_info             # noqa: E402


def venues_missing_capacity(conn):
    return conn.execute(
        """SELECT v.venue_id, v.venue_name,
                  (SELECT m.cb_match_id FROM matches m
                    WHERE m.venue_id = v.venue_id AND m.cb_match_id IS NOT NULL
                    ORDER BY m.match_date DESC LIMIT 1) AS cb_match_id,
                  COALESCE((SELECT SUM(m.match_type = 'International')
                              FROM matches m WHERE m.venue_id = v.venue_id), 0)
                      AS intl,
                  (SELECT COUNT(*) FROM matches m
                    WHERE m.venue_id = v.venue_id) AS n
           FROM venues v
           WHERE v.capacity IS NULL AND v.cb_venue_id IS NOT NULL
           ORDER BY intl DESC, n DESC, v.venue_name""").fetchall()


def run(conn, fetch, max_calls):
    stats = {"checked": 0, "found": 0, "calls": 0, "stopped": None}
    for venue_id, name, cb_match_id, _, _ in venues_missing_capacity(conn):
        if cb_match_id is None:
            continue
        try:
            payload, used = fetch(cb_match_id, stats["calls"] < max_calls)
        except CricbuzzAPIError as exc:
            stats["stopped"] = f"API error: {exc}"
            break
        if payload is None:
            stats["stopped"] = "call budget reached"
            break
        stats["calls"] += 1 if used else 0
        stats["checked"] += 1
        parse_match_info(conn, cb_match_id, payload)
        cap = conn.execute("SELECT capacity FROM venues WHERE venue_id = ?",
                           (venue_id,)).fetchone()[0]
        if cap:
            stats["found"] += 1
            print(f"  {name}: capacity {cap:,}"
                  f"{'' if used else '  (from cache)'}")
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-calls", type=int, default=30)
    args = ap.parse_args()
    client = CricbuzzClient()

    def fetch(cb_match_id, allowed):
        path = f"/mcenter/v1/{cb_match_id}"
        cached = raw_store.get(path)
        if cached is not None:
            return cached, False
        if not allowed:
            return None, False
        payload = client.get(path, None)
        raw_store.put(path, None, payload)
        return payload, True

    with get_connection() as conn:
        s = run(conn, fetch, args.max_calls)
        left = len(venues_missing_capacity(conn))
        big = conn.execute(
            "SELECT COUNT(*) FROM venues WHERE capacity > 50000").fetchone()[0]
    print(f"\nVenues checked: {s['checked']} | capacity found: {s['found']} "
          f"| API calls: {s['calls']}")
    print(f"Still without capacity: {left} | venues over 50,000: {big}")
    if s["stopped"]:
        print("Stopped:", s["stopped"], "(run again later to continue)")


if __name__ == "__main__":
    main()