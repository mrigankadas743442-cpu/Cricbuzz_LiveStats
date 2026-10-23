"""Print the shape of a saved API response (reads the local cache only).

Usage (from the project root):
    python scripts/inspect_cache.py /mcenter/v1/151602/scard
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services import raw_store

MAX_DEPTH = 6
MAX_KEYS = 12


def shape(x, depth=0):
    pad = "  " * depth
    if isinstance(x, dict):
        items = list(x.items())
        for k, v in items[:MAX_KEYS]:
            if isinstance(v, (dict, list)) and depth < MAX_DEPTH:
                print(f"{pad}{k}: {type(v).__name__}[{len(v)}]")
                shape(v, depth + 1)
            else:
                print(f"{pad}{k}: {repr(v)[:60]}")
        if len(items) > MAX_KEYS:
            print(f"{pad}... {len(items) - MAX_KEYS} more keys")
    elif isinstance(x, list) and x:
        print(f"{pad}[first item]")
        shape(x[0], depth + 1)


path = sys.argv[1]
data = raw_store.get(path)
if data is None:
    print("Not in cache:", path)
else:
    shape(data)