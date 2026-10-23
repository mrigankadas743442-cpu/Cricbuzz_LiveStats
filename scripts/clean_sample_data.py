"""Remove the seed/sample rows (Sample Player ..., seed matches, venues, series).

  python scripts/clean_sample_data.py           dry run: only shows counts
  python scripts/clean_sample_data.py --apply   backs up the database first,
                                                then deletes

Each backup gets its own timestamped name, so an earlier backup is never
overwritten.
"""
import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import DB_PATH, get_connection  # noqa: E402

SAMPLE_PLAYERS = "full_name LIKE 'Sample Player%'"
SEED_MATCHES = "cb_match_id IS NULL"
# Seed venues/series have no Cricbuzz ID and no real match pointing at them.
SEED_VENUES = ("cb_venue_id IS NULL AND venue_id NOT IN "
               "(SELECT venue_id FROM matches WHERE venue_id IS NOT NULL)")
SEED_SERIES = ("cb_series_id IS NULL AND series_id NOT IN "
               "(SELECT series_id FROM matches WHERE series_id IS NOT NULL)")


def counts(conn) -> dict:
    one = lambda sql: conn.execute(sql).fetchone()[0]
    return {
        "sample players": one(f"SELECT COUNT(*) FROM players WHERE {SAMPLE_PLAYERS}"),
        "seed matches": one(f"SELECT COUNT(*) FROM matches WHERE {SEED_MATCHES}"),
        "career-stat rows of sample players": one(
            f"""SELECT COUNT(*) FROM player_career_stats WHERE player_id IN
                (SELECT player_id FROM players WHERE {SAMPLE_PLAYERS})"""),
        "seed venues": one(f"SELECT COUNT(*) FROM venues WHERE {SEED_VENUES}"),
        "seed series": one(f"SELECT COUNT(*) FROM series WHERE {SEED_SERIES}"),
    }


def clean(conn) -> None:
    ids = f"(SELECT player_id FROM players WHERE {SAMPLE_PLAYERS})"
    # Seed matches first: innings, scorecards and fielding cascade from them.
    conn.execute(f"DELETE FROM matches WHERE {SEED_MATCHES}")
    for table in ("batting_scorecard", "bowling_scorecard", "fielding_stats",
                  "player_career_stats"):
        conn.execute(f"DELETE FROM {table} WHERE player_id IN {ids}")
    conn.execute(f"DELETE FROM players WHERE {SAMPLE_PLAYERS}")
    conn.execute(f"DELETE FROM venues WHERE {SEED_VENUES}")
    conn.execute(f"DELETE FROM series WHERE {SEED_SERIES}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    with get_connection() as conn:
        print("Found:", counts(conn))
        if not args.apply:
            print("Dry run only. Add --apply to delete (a backup is made).")
            return
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = Path(DB_PATH).with_name(f"cricket.backup-{stamp}.db")
    shutil.copyfile(DB_PATH, backup)
    print("Backup saved:", backup)
    with get_connection() as conn:
        clean(conn)
        print("After :", counts(conn))


if __name__ == "__main__":
    main()