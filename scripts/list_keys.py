"""List every top-level key of a saved API response (local cache only).

Usage (from the project root):
    python scripts/list_keys.py /mcenter/v1/151602
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services import raw_store

data = raw_store.get(sys.argv[1])
if data is None:
    print("Not in cache")
else:
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{key}: dict -> {list(value.keys())}")
        elif isinstance(value, list):
            print(f"{key}: list[{len(value)}]")
        else:
            print(f"{key}: {repr(value)[:50]}")