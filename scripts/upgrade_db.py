"""One-time upgrade: add matches.match_type and move the API cache.

Usage (from the project root):
    python scripts/upgrade_db.py
Safe to run more than once.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import DB_PATH
from services import raw_store

conn = sqlite3.connect(DB_PATH)

columns = [r[1] for r in conn.execute("PRAGMA table_info(matches)")]
if "match_type" not in columns:
    conn.execute("ALTER TABLE matches ADD COLUMN match_type TEXT")
    conn.commit()
    print("Added matches.match_type")
else:
    print("matches.match_type already exists")

try:
    rows = conn.execute(
        "SELECT cache_key, path, body, fetched_at FROM api_cache").fetchall()
except sqlite3.OperationalError:
    rows = []
    print("No old api_cache table found in cricket.db (nothing to copy).")
conn.close()

if rows:
    raw_store.import_rows(rows)
    print(f"Copied {len(rows)} cached responses to {raw_store.CACHE_PATH}")