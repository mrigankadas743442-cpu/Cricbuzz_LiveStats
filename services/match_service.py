"""Live-match data for the Live Matches page. API in, plain dicts out."""
from typing import Any

from api.cricbuzz_client import CricbuzzClient
from services import raw_store


def _score_text(score: dict | None) -> str:
    """Build '210/3 (45.2 ov)' text from a team score block."""
    if not score:
        return "Yet to bat"
    parts = []
    for key in ("inngs1", "inngs2"):
        inn = score.get(key)
        if inn:
            wk = inn.get("wickets", 10)
            parts.append(f"{inn.get('runs', 0)}/{wk} ({inn.get('overs', 0)} ov)")
    return " & ".join(parts) or "Yet to bat"


def parse_matches(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten a /matches/v1/* payload into a list of simple dicts."""
    out: list[dict[str, Any]] = []
    for block in payload.get("typeMatches", []):
        for series in block.get("seriesMatches", []):
            wrapper = series.get("seriesAdWrapper") or {}
            for m in wrapper.get("matches", []):
                info = m.get("matchInfo") or {}
                score = m.get("matchScore") or {}
                venue = info.get("venueInfo") or {}
                out.append({
                    "match_id": info.get("matchId"),
                    "series": wrapper.get("seriesName", ""),
                    "description": info.get("matchDesc", ""),
                    "format": info.get("matchFormat", ""),
                    "state": info.get("state", ""),
                    "status": info.get("status", ""),
                    "team1": (info.get("team1") or {}).get("teamName", "?"),
                    "team2": (info.get("team2") or {}).get("teamName", "?"),
                    "score1": _score_text(score.get("team1Score")),
                    "score2": _score_text(score.get("team2Score")),
                    "venue": ", ".join(
                        x for x in (venue.get("ground"), venue.get("city")) if x
                    ) or "Venue not available",
                })
    return [m for m in out if m["match_id"]]


def fetch_matches(kind: str) -> list[dict[str, Any]]:
    """kind: 'live' or 'recent'. Raises CricbuzzAPIError on failure."""
    client = CricbuzzClient()
    payload = client.live_matches() if kind == "live" else client.recent_matches()
    return parse_matches(payload)


def parse_scorecard(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """One dict per innings, using this API's lowercase field names."""
    innings_list = []
    for number, inn in enumerate(payload.get("scorecard") or [], start=1):
        batting = [
            {"Batter": b.get("name"), "Dismissal": b.get("outdec"),
             "R": b.get("runs"), "B": b.get("balls"), "4s": b.get("fours"),
             "6s": b.get("sixes"), "SR": b.get("strkrate")}
            for b in inn.get("batsman") or []
            if (b.get("outdec") or "").strip()      # skip did-not-bat
        ]
        bowling = [
            {"Bowler": w.get("name"), "O": w.get("overs"),
             "M": w.get("maidens"), "R": w.get("runs"),
             "W": w.get("wickets"), "Econ": w.get("economy")}
            for w in inn.get("bowler") or []
        ]
        extras = inn.get("extras") or {}
        innings_list.append({
            "title": f"Innings {number}: {inn.get('batteamname', 'Team')}",
            "total": f"{inn.get('score', 0)}/{inn.get('wickets', 0)} "
                     f"({inn.get('overs', 0)} ov)",
            "extras": extras.get("total", 0),
            "batting": batting,
            "bowling": bowling,
        })
    return innings_list


def fetch_scorecard(match_id: int, complete: bool = False) -> list[dict[str, Any]]:
    """Finished matches come from the saved cache when possible (no quota).

    Live matches always hit the API because scores change. Every API
    response is saved, so it is never lost.
    """
    path = f"/mcenter/v1/{match_id}/scard"
    payload = raw_store.get(path) if complete else None
    if payload is None:
        payload = CricbuzzClient().scorecard(match_id)
        raw_store.put(path, None, payload)
    return parse_scorecard(payload)