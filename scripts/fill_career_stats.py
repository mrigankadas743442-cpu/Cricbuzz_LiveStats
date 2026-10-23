"""Fill player_career_stats from the Top Stats leaderboards.

Q3, Q7, Q9, Q11, Q20 and Q21 read career statistics. Right now that table
holds only sample rows. The Top Stats leaderboards (which already work in
your app) contain the real numbers for the top players, so we save them.

Each leaderboard (category x format) is ONE API call and is cached, so
re-running costs nothing.

  python scripts/fill_career_stats.py --dry-run
      Fetches (and caches) the leaderboards, prints which table column each
      leaderboard column maps to, and writes nothing.

  python scripts/fill_career_stats.py
      Does the same and saves the rows.

  python scripts/fill_career_stats.py --max-calls 9
      Stop after 9 API calls (run again after your quota resets).

  python scripts/fill_career_stats.py --repair
      One-off repair: clears batting average, bowling average and wickets of
      real players, then refills them from the cached leaderboards
      (needs no API calls).
"""
import argparse
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.cricbuzz_client import CricbuzzAPIError   # noqa: E402
from database.connection import get_connection      # noqa: E402
from services import player_service as ps           # noqa: E402
from services import raw_store                       # noqa: E402

# leaderboard category (matched by keyword in its label)
#   -> {player_career_stats column: regex for the leaderboard header}
TARGETS = [
    # Order matters: the first keyword found in the label wins, so the
    # specific "bowling average" must come before the generic "average".
    # An empty mapping means "ignore this leaderboard" ("5-wicket hauls"
    # counts hauls, not career wickets, so it must never reach 'wickets').
    ("haul",    {}),
    ("runs",    {"runs": r"^runs$", "matches_played": r"^(matches|mat)",
                 "strike_rate": r"strike|^sr$"}),
    ("score",   {"highest_score": r"score|^hs$"}),
    ("bowling average", {"bowling_avg": r"avg|average"}),
    ("average", {"batting_avg": r"avg|average"}),
    ("hundred", {"centuries": r"hundred|100|centur"}),
    ("wicket",  {"wickets": r"^wick|^wkts", "matches_played": r"^(matches|mat)",
                 "bowling_avg": r"avg|average", "economy": r"econ"}),
    ("econ",    {"economy": r"econ"}),
]
ID_RE = re.compile(r"^(player\s*)?id$", re.I)
NAME_RE = re.compile(r"^(player|name|batsman|bowler)(\s*name)?$", re.I)
ALLOWED = {"runs", "matches_played", "strike_rate", "highest_score",
           "batting_avg", "centuries", "wickets", "bowling_avg", "economy"}


def targets_for(category: str) -> dict:
    label = category.lower()
    for keyword, mapping in TARGETS:
        if keyword in label:
            return mapping
    return {}


def find_col(df, pattern):
    rx = re.compile(pattern, re.I)
    for col in df.columns:
        name = str(col).strip()
        if ID_RE.match(name) or NAME_RE.match(name):
            continue
        if rx.search(name):
            return col
    return None


def id_and_name_columns(df):
    pid = next((c for c in df.columns if ID_RE.match(str(c).strip())), None)
    name = next((c for c in df.columns if NAME_RE.match(str(c).strip())), None)
    return pid, name


def get_leaderboard(category, fmt, allowed):
    """Return (DataFrame or None, used_api_call). Cached after first fetch."""
    path = f"/saved-topstats/{category}/{fmt}"
    cached = raw_store.get(path)
    if cached is not None:
        return pd.DataFrame(cached["rows"], columns=cached["columns"]), False
    if not allowed:
        return None, False
    df = ps.fetch_top_stats_api(category, fmt)
    rows = df.astype(object).where(df.notna(), None).values.tolist()
    raw_store.put(path, None, {"columns": [str(c) for c in df.columns],
                               "rows": rows})
    return df, True


def player_id_for(conn, cb_id, name):
    row = conn.execute("SELECT player_id FROM players WHERE cb_player_id = ?",
                       (cb_id,)).fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO players (cb_player_id, full_name, country) "
        "VALUES (?, ?, 'Unknown')", (cb_id, name))
    return cur.lastrowid


def save_rows(conn, df, fmt, mapping, pid_col, name_col):
    """Upsert one leaderboard. Only the mapped columns are touched."""
    cols = {target: find_col(df, rx) for target, rx in mapping.items()}
    cols = {t: c for t, c in cols.items() if c is not None and t in ALLOWED}
    if not cols or pid_col is None or name_col is None:
        return 0, cols
    saved = 0
    for _, row in df.iterrows():
        cb_id = pd.to_numeric(row[pid_col], errors="coerce")
        if pd.isna(cb_id):
            continue
        pid = player_id_for(conn, int(cb_id), str(row[name_col]).strip())
        values = {}
        for target, col in cols.items():
            number = pd.to_numeric(row[col], errors="coerce")
            if not pd.isna(number):
                values[target] = (int(number) if float(number).is_integer()
                                  and target not in ("batting_avg",
                                                     "bowling_avg",
                                                     "strike_rate", "economy")
                                  else float(number))
        if not values:
            continue
        names = list(values)
        conn.execute(
            f"""INSERT INTO player_career_stats (player_id, format,
                    {', '.join(names)})
                VALUES (?, ?, {', '.join('?' * len(names))})
                ON CONFLICT(player_id, format) DO UPDATE SET
                    {', '.join(f'{n} = excluded.{n}' for n in names)}""",
            (pid, fmt, *values.values()))
        saved += 1
    return saved, cols


def run(conn, fetch, categories, formats, max_calls, dry_run):
    summary = {"calls": 0, "rows": 0, "stopped": None, "skipped": []}
    for category in categories:
        mapping = targets_for(category)
        if not mapping:
            summary["skipped"].append(category)
            continue
        for fmt in formats:
            try:
                df, used = fetch(category, fmt, summary["calls"] < max_calls)
            except CricbuzzAPIError as exc:
                summary["stopped"] = f"API error: {exc}"
                return summary
            if df is None:
                summary["stopped"] = "call budget reached"
                return summary
            summary["calls"] += 1 if used else 0
            pid_col, name_col = id_and_name_columns(df)
            if dry_run:
                found = {t: find_col(df, rx) for t, rx in mapping.items()}
                print(f"[{category} / {fmt}] {len(df)} rows | columns: "
                      f"{list(df.columns)}")
                print(f"    id={pid_col!r} name={name_col!r} maps: {found}")
                continue
            saved, cols = save_rows(conn, df, fmt, mapping, pid_col, name_col)
            summary["rows"] += saved
            print(f"[{category} / {fmt}] saved {saved} rows -> "
                  f"{sorted(cols) or 'NOTHING MAPPED'}"
                  f"{'' if used else '  (from cache)'}")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-calls", type=int, default=18)
    ap.add_argument("--repair", action="store_true")
    args = ap.parse_args()

    def fetch(category, fmt, allowed):
        return get_leaderboard(category, fmt, allowed)

    with get_connection() as conn:
        if args.repair:
            conn.execute(
                """UPDATE player_career_stats
                   SET batting_avg = NULL, bowling_avg = NULL, wickets = 0
                   WHERE player_id IN (SELECT player_id FROM players
                                       WHERE full_name NOT LIKE 'Sample Player%')""")
            print("Cleared averages and wickets of real players; refilling...")
        s = run(conn, fetch, list(ps.CATEGORIES), list(ps.FORMAT_IDS),
                args.max_calls, args.dry_run)
    print(f"\nAPI calls: {s['calls']} | rows saved: {s['rows']}")
    if s["skipped"]:
        print("Categories with no mapping (ignored):", s["skipped"])
    if s["stopped"]:
        print("Stopped:", s["stopped"], "(run again later to continue)")


if __name__ == "__main__":
    main()