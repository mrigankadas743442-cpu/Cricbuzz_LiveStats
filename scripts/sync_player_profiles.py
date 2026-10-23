
"""Sync existing player profiles from Cricbuzz into SQLite."""

import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.cricbuzz_client import CricbuzzClient, CricbuzzAPIError
from database.connection import get_connection


def clean(value):
    """Convert blank strings to None."""
    if not isinstance(value, str):
        return value
    value = value.strip()
    return value or None


def parse_dob(value):
    """Convert Cricbuzz's date format to an ISO date when possible."""
    value = clean(value)
    if not value:
        return None

    # The API may return either a formatted date or a date with age.
    value = re.sub(r"\s*\([^)]*\)\s*$", "", value).strip()

    for fmt in ("%B %d, %Y", "%d %B %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue

    return None


def sync_profiles():
    client = CricbuzzClient()

    with get_connection() as conn:
        players = conn.execute("""
            SELECT player_id, cb_player_id, full_name, country,
                   playing_role, batting_style, bowling_style,
                   date_of_birth
            FROM players
            WHERE playing_role IS NULL
               OR batting_style IS NULL
               OR bowling_style IS NULL
               OR cb_player_id IS NULL
            ORDER BY full_name
        """).fetchall()

    updated = 0
    skipped = 0
    failed = 0

    for player in players:
        name = player["full_name"]
        print(f"Searching Cricbuzz: {name}")

        try:
            profile = client.search_player(name)
        except CricbuzzAPIError as exc:
            print(f"  API request failed: {exc}")
            failed += 1
            continue

        if not isinstance(profile, dict):
            print("  Skipped: unexpected API response.")
            skipped += 1
            continue

        api_name = clean(profile.get("fullName")) or clean(profile.get("name"))
        api_id = clean(profile.get("id"))

        # Never update a database row from a different player's profile.
        if not api_name or api_name.casefold() != name.strip().casefold():
            print(f"  Skipped: returned name does not match ({api_name!r}).")
            skipped += 1
            continue

        try:
            cb_player_id = int(api_id) if api_id else None
        except (ValueError, TypeError):
            cb_player_id = None

        api_country = clean(profile.get("intlTeam"))
        role = clean(profile.get("role"))
        batting = clean(profile.get("bat"))
        bowling = clean(profile.get("bowl"))
        dob = parse_dob(profile.get("DoBFormat") or profile.get("DoB"))

        # Only fill missing values; do not overwrite existing information
        # with blank or unavailable API fields.
        values = {
            "cb_player_id": cb_player_id,
            "country": api_country,
            "playing_role": role,
            "batting_style": batting,
            "bowling_style": bowling,
            "date_of_birth": dob,
        }

        with get_connection() as conn:
            current = conn.execute(
                "SELECT * FROM players WHERE player_id = ?",
                (player["player_id"],),
            ).fetchone()

            if current is None:
                skipped += 1
                continue

            updates = {}
            for column, value in values.items():
                if value is not None and not current[column]:
                    updates[column] = value

            if updates:
                assignments = ", ".join(
                    f"{column} = ?" for column in updates
                )
                params = list(updates.values()) + [player["player_id"]]

                try:
                    conn.execute(
                        f"UPDATE players SET {assignments} WHERE player_id = ?",
                        params,
                    )
                    updated += 1
                    print(f"  Updated: {', '.join(updates.keys())}")
                except Exception as exc:
                    print(f"  Could not update {name}: {exc}")
                    failed += 1
            else:
                print("  No missing fields were available to fill.")
                skipped += 1

    print("\nProfile sync finished.")
    print(f"Players checked: {len(players)}")
    print(f"Rows updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    sync_profiles()
