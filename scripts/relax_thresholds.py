"""Lower the minimum-data thresholds of six SQL questions to fit a small dataset.

The questions ask for things like ">= 10 matches per bowler". Your harvested
data covers about two weeks, so those minimums can never be met. This script
changes each minimum to 2 and writes a comment at the top of the file saying
so, so a reviewer can see it is a deliberate choice. Safe to run twice.

  python scripts/relax_thresholds.py            show what would change
  python scripts/relax_thresholds.py --apply    edit the files
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ROOT / "sql" / "queries"

# file prefix -> (exact old text, new text, original minimum)
EDITS = {
    "q14": ("HAVING COUNT(DISTINCT m.match_id) >= 3",
            "HAVING COUNT(DISTINCT m.match_id) >= 2", 3),
    "q16": ("HAVING COUNT(DISTINCT m.match_id) >= 5",
            "HAVING COUNT(DISTINCT m.match_id) >= 2", 5),
    "q18": ("HAVING COUNT(DISTINCT s.match_id) >= 10",
            "HAVING COUNT(DISTINCT s.match_id) >= 2", 10),
    "q22a": ("HAVING COUNT(*) >= 5", "HAVING COUNT(*) >= 2", 5),
    "q22b": ("HAVING COUNT(*) >= 5", "HAVING COUNT(*) >= 2", 5),
    "q23": ("HAVING COUNT(*) >= 5", "HAVING COUNT(*) >= 2", 5),
    "q24": ("HAVING COUNT(*) >= 5", "HAVING COUNT(*) >= 2", 5),
}
MARK = "-- Threshold relaxed"


def find_file(prefix):
    matches = sorted(QUERIES.glob(f"{prefix}.sql")) or \
        sorted(QUERIES.glob(f"{prefix}_*.sql"))
    return matches[0] if matches else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    for prefix, (old, new, original) in EDITS.items():
        path = find_file(prefix)
        if path is None:
            print(f"{prefix}: file not found in {QUERIES}")
            continue
        text = path.read_text(encoding="utf-8")
        if MARK in text:
            print(f"{path.name}: already relaxed")
            continue
        if text.count(old) != 1:
            print(f"{path.name}: expected line not found exactly once "
                  f"({text.count(old)} found); edit by hand: {old!r}")
            continue
        print(f"{path.name}: minimum {original} -> 2")
        if args.apply:
            note = (f"{MARK} from {original} to 2: the harvested data covers "
                    f"only a few weeks.\n"
                    f"-- Restore '{old}' once more history is loaded.\n")
            path.write_text(note + text.replace(old, new), encoding="utf-8")
    if not args.apply:
        print("\nDry run. Add --apply to edit the files.")


if __name__ == "__main__":
    main()