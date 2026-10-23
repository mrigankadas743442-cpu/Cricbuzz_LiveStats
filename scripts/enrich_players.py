"""Fill playing role, batting style and bowling style from player profiles.

Scorecards only carry names and scores, so these three fields start empty.
Each profile costs ONE API call and is saved in the raw cache, so a player
is never fetched twice.

  python scripts/enrich_players.py --probe
      One call: shows what the profile endpoint returns. Writes nothing.

  python scripts/enrich_players.py --country India --max-calls 15
      Fills players whose country is India, up to 15 API calls.

  python scripts/enrich_players.py --all --max-calls 30
      Any country.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.cricbuzz_client import CricbuzzAPIError, CricbuzzClient  # noqa: E402
from database.connection import get_connection                    # noqa: E402
from services import raw_store                                      # noqa: E402
from utils.logger import get_logger                                 # noqa: E402
from utils.validators import ROLES                                  # noqa: E402

log = get_logger(__name__)


def profile_path(cb_player_id: int) -> str:
    return f"/stats/v1/player/{cb_player_id}"


def _pick(payload: dict, *keys):
    """First non-empty string among several possible key names."""
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def normalize_role(raw):
    """Map Cricbuzz wording ('WK-Batsman', 'Batting Allrounder', ...) onto
    the role names the app accepts (utils.validators.ROLES)."""
    if not raw:
        return None
    text = raw.lower().replace("-", "").replace(" ", "")
    if "wk" in text or "keeper" in text:
        keyword = "keeper"
    elif "allrounder" in text:
        keyword = "all"
    elif "bowl" in text:
        keyword = "bowl"
    elif "bat" in text:
        keyword = "bat"
    else:
        return raw if raw in ROLES else None
    for allowed in sorted(ROLES):
        if keyword in allowed.lower().replace("-", "").replace(" ", ""):
            return allowed
    return raw if raw in ROLES else None


def parse_profile(payload: dict) -> dict:
    return {
        "role": normalize_role(_pick(payload, "role", "playingRole")),
        "bat": _pick(payload, "bat", "battingStyle"),
        "bowl": _pick(payload, "bowl", "bowlingStyle"),
    }


def candidates(conn, country):
    return conn.execute(
        """SELECT player_id, cb_player_id, full_name FROM players
           WHERE cb_player_id IS NOT NULL
             AND full_name NOT LIKE 'Sample Player%'
             AND (playing_role IS NULL OR batting_style IS NULL
                  OR bowling_style IS NULL)
             AND (? IS NULL OR country = ?)
           ORDER BY full_name""", (country, country)).fetchall()


def enrich(conn, fetch, country, max_calls):
    """fetch(cb_player_id, allowed) -> (payload, used_api_call)."""
    rows = candidates(conn, country)
    stats = {"candidates": len(rows), "updated": 0, "empty": 0,
             "calls": 0, "stopped": None}
    for player_id, cb_id, name in rows:
        try:
            payload, used = fetch(cb_id, stats["calls"] < max_calls)
        except CricbuzzAPIError as exc:
            stats["stopped"] = f"API error: {exc}"
            break
        if payload is None:                      # call budget used up
            stats["stopped"] = "call budget reached"
            break
        stats["calls"] += 1 if used else 0
        info = parse_profile(payload)
        if not any(info.values()):
            stats["empty"] += 1
            log.warning("No profile fields for %s (%s)", name, cb_id)
            continue
        conn.execute(
            """UPDATE players SET
                   playing_role  = COALESCE(?, playing_role),
                   batting_style = COALESCE(?, batting_style),
                   bowling_style = COALESCE(?, bowling_style)
               WHERE player_id = ?""",
            (info["role"], info["bat"], info["bowl"], player_id))
        stats["updated"] += 1
        print(f"  {name}: {info['role']} | {info['bat']} | {info['bowl']}"
              f"{'' if used else '  (from cache)'}")
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--country", default="India")
    ap.add_argument("--all", action="store_true", help="any country")
    ap.add_argument("--max-calls", type=int, default=15)
    args = ap.parse_args()
    country = None if args.all else args.country
    client = CricbuzzClient()

    def fetch(cb_id, allowed):
        path = profile_path(cb_id)
        cached = raw_store.get(path)
        if cached is not None:
            return cached, False
        if not allowed:
            return None, False
        payload = client.get(path, None)
        raw_store.put(path, None, payload)
        return payload, True

    with get_connection() as conn:
        if args.probe:
            rows = candidates(conn, country)
            if not rows:
                print("No players need profile data.")
                return
            _, cb_id, name = rows[0]
            print(f"Probing {name} (cb id {cb_id}). Roles the app accepts: "
                  f"{sorted(ROLES)}")
            payload, _ = fetch(cb_id, True)
            print("Top-level keys:", sorted(payload))
            print("Parsed:", parse_profile(payload))
            print(json.dumps(payload, indent=1)[:1500])
            return

        stats = enrich(conn, fetch, country, args.max_calls)
    print(f"\nCandidates: {stats['candidates']} | updated: {stats['updated']} "
          f"| no data: {stats['empty']} | API calls: {stats['calls']}")
    if stats["stopped"]:
        print("Stopped:", stats["stopped"], "(run again later to continue)")


if __name__ == "__main__":
    main()