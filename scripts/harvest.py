"""Download API data into the local cache within a call budget.

Usage (from the project root):
    python scripts/harvest.py --max-calls 30
Re-run any time: saved items are skipped and cost nothing.
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.cricbuzz_client import CricbuzzAPIError, CricbuzzClient
from services import raw_store
from services.ingestion_service import ingest_matches
from services.match_service import parse_matches

parser = argparse.ArgumentParser()
parser.add_argument("--max-calls", type=int, default=30)
parser.add_argument("--sleep", type=float, default=1.2,
                    help="seconds between calls (be polite to the API)")
args = parser.parse_args()

client = CricbuzzClient()
calls = 0


class StopHarvest(Exception):
    pass


def fetch(path, params=None, max_age_hours=None):
    """Cache first; call the API only if needed and budget allows."""
    global calls
    cached = raw_store.get(path, params, max_age_hours)
    if cached is not None:
        return cached
    if calls >= args.max_calls:
        raise StopHarvest("call budget reached")
    try:
        data = client.get(path, params)
    except CricbuzzAPIError as exc:
        if "429" in str(exc):
            raise StopHarvest("rate limit or monthly quota reached") from exc
        print(f"  skipped {path}: {exc}")
        return None
    calls += 1
    raw_store.put(path, params, data)
    print(f"  saved {path} (call {calls}/{args.max_calls})")
    time.sleep(args.sleep)
    return data


try:
    recent = fetch("/matches/v1/recent", max_age_hours=12)
    if recent:
        print("Matches saved to tables:", ingest_matches(recent))
        done = [m for m in parse_matches(recent)
                if m["state"].lower().startswith("complete")]
        print(f"{len(done)} completed matches to collect")
        for m in done:
            fetch(f"/mcenter/v1/{m['match_id']}")        # toss, result, venue
            fetch(f"/mcenter/v1/{m['match_id']}/scard")  # innings, players
except StopHarvest as stop:
    print("Stopped:", stop)

print(f"Calls used this run: {calls}")