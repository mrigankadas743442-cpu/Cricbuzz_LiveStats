
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

CRICBUZZ_API_KEY = os.getenv("CRICBUZZ_API_KEY", "")
CRICBUZZ_API_HOST = os.getenv(
    "CRICBUZZ_API_HOST",
    "cricbuzz-cricket2.p.rapidapi.com",
)

# Compatibility with existing services
RAPIDAPI_KEY = CRICBUZZ_API_KEY
RAPIDAPI_HOST = CRICBUZZ_API_HOST

# Cricbuzz API base URL
BASE_URL = f"https://{CRICBUZZ_API_HOST}"

MAX_RETRIES = 3
REQUEST_TIMEOUT = 20
