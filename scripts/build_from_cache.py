"""Fill the tables from saved API responses (no API calls, no quota).

Usage (from the project root):
    python scripts/build_from_cache.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_connection
from services import raw_store
from services.cache_parser import parse_scorecard
from services.ingestion_service import ingest_matches
from services.match_info_parser import (apply_results_from_status,
                                        parse_match_info)

SCARD = re.compile(r"^/mcenter/v1/(\d+)/scard$")
INFO = re.compile(r"^/mcenter/v1/(\d+)$")

recent = raw_store.get("/matches/v1/recent")
if recent:
    print("Matches saved:", ingest_matches(recent))
else:
    print("No match list in the cache. Run harvest.py first.")

with get_connection() as conn:
    innings = infos = 0
    for path, payload in raw_store.items("/mcenter/v1/%"):
        m = SCARD.match(path)
        if m:
            innings += parse_scorecard(conn, int(m.group(1)), payload)
            continue
        m = INFO.match(path)
        if m and parse_match_info(conn, int(m.group(1)), payload):
            infos += 1
    understood, unparsed = apply_results_from_status(conn)

    print(f"Innings saved: {innings} | match-info files applied: {infos}")
    print(f"Match results understood from status text: {understood}")
    if unparsed:
        print("Status texts NOT understood (send me these):")
        for s in unparsed:
            print("   ", repr(s))
    for label, sql in (
        ("matches with a winner", "SELECT COUNT(*) FROM matches WHERE winner_id IS NOT NULL"),
        ("matches with toss info", "SELECT COUNT(*) FROM matches WHERE toss_winner_id IS NOT NULL"),
        ("venues with a country", "SELECT COUNT(*) FROM venues WHERE country IS NOT NULL"),
        ("venues with capacity", "SELECT COUNT(*) FROM venues WHERE capacity IS NOT NULL"),
        ("innings", "SELECT COUNT(*) FROM innings"),
        ("batting rows", "SELECT COUNT(*) FROM batting_scorecard"),
    ):
        print(f"  {label}: {conn.execute(sql).fetchone()[0]}")