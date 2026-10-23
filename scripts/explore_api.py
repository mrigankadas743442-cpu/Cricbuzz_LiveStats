import json
from pathlib import Path
from api.cricbuzz_client import CricbuzzClient

data = CricbuzzClient().recent_matches()
out = Path("data/raw"); out.mkdir(parents=True, exist_ok=True)
(out / "recent.json").write_text(json.dumps(data, indent=2))
print(list(data.keys()))