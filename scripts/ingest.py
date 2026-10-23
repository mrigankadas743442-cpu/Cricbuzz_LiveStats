
from api.cricbuzz_client import CricbuzzClient
from services.ingestion_service import ingest_matches

print(ingest_matches(CricbuzzClient().recent_matches()), "matches saved")