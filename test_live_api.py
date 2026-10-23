
from api.cricbuzz_client import CricbuzzClient, CricbuzzAPIError

try:
    client = CricbuzzClient()
    data = client.live_matches()

    print("API connection successful!")
    print("Top-level keys:", list(data.keys()))
    print("Has typeMatches:", "typeMatches" in data)

except CricbuzzAPIError as exc:
    print("API request failed:", exc)
except Exception as exc:
    print(f"Unexpected error: {type(exc).__name__}: {exc}")
