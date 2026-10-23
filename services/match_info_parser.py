"""Fill winner, margin, toss, venue and team country from saved data.

Reads only the local database and cached responses; no API calls.
"""
import re

_TOSS = re.compile(
    r"^(?P<team>.+?)\s+(?:opt(?:ed)?|elected|chose)\s+to\s+(?P<dec>bat|bowl|field)",
    re.I)
_WON_RUNS = re.compile(
    r"^(?P<team>.+?)\s+won\s+by\s+(?:an\s+innings\s+and\s+)?(?P<n>\d+)\s+runs?", re.I)
_WON_WKTS = re.compile(
    r"^(?P<team>.+?)\s+won\s+by\s+(?P<n>\d+)\s+(?:wkts?|wickets?)", re.I)


def _norm(text):
    """Lowercase and collapse repeated spaces so 'A  -  B' equals 'A - B'."""
    return " ".join((text or "").lower().split())


def _find_team(text, teams):
    """teams: list of (team_id, team_name). Exact match first, then loose."""
    text = _norm(text)
    for tid, name in teams:
        if _norm(name) == text:
            return tid
    for tid, name in teams:
        n = _norm(name)
        if text and (text in n or n in text):
            return tid
    return None


def parse_result(status, teams):
    """Return (winner_id, margin, victory_type), or None if not understood."""
    s = (status or "").strip()
    for rx, vtype in ((_WON_RUNS, "runs"), (_WON_WKTS, "wickets")):
        m = rx.match(s)
        if m:
            winner = _find_team(m.group("team"), teams)
            return (winner, int(m.group("n")), vtype) if winner else None

    forfeit = re.match(
        r"^(?P<team>.+?)\s+(?:are|is)\s+deemed\s+to\s+have\s+forfeited", s, re.I)
    if forfeit:
        loser = _find_team(forfeit.group("team"), teams)
        winner = next((tid for tid, _ in teams if tid != loser), None) if loser else None
        return (winner, None, None) if winner else None
    low = s.lower()
    if "no result" in low or "abandon" in low:
        return (None, None, None)          # known: nobody won
    if "drawn" in low or low.endswith("draw"):
        return (None, None, "draw")
    if "tied" in low:
        return (None, None, "tie")
    return None


def apply_results_from_status(conn):
    """Set winner/margin/type on every match from its status text.

    Returns (understood, examples_of_unparsed_status_text).
    """
    rows = conn.execute(
        """SELECT m.match_id, m.status, m.team1_id, t1.team_name,
                  m.team2_id, t2.team_name
           FROM matches m
           JOIN teams t1 ON t1.team_id = m.team1_id
           JOIN teams t2 ON t2.team_id = m.team2_id
           WHERE m.cb_match_id IS NOT NULL AND m.status IS NOT NULL""").fetchall()
    understood, unparsed = 0, []
    for r in rows:
        result = parse_result(r[1], [(r[2], r[3]), (r[4], r[5])])
        if result is None:
            if r[1] not in unparsed and len(unparsed) < 10:
                unparsed.append(r[1])
            continue
        conn.execute(
            """UPDATE matches SET winner_id = ?, victory_margin = ?,
                                  victory_type = ? WHERE match_id = ?""",
            (*result, r[0]))
        understood += 1
    return understood, unparsed


def parse_match_info(conn, cb_match_id, payload):
    """Apply toss, venue and team-country details from a /mcenter/v1/{id}
    payload. Returns False if the match is not in the database."""
    match = conn.execute(
        "SELECT match_id, team1_id, team2_id FROM matches WHERE cb_match_id = ?",
        (cb_match_id,)).fetchone()
    if match is None:
        return False
    match_id = match[0]
    teams = [(r[0], r[1]) for r in conn.execute(
        "SELECT team_id, team_name FROM teams WHERE team_id IN (?, ?)",
        (match[1], match[2]))]

    toss = _TOSS.match(payload.get("tossstatus") or "")
    if toss:
        winner = _find_team(toss.group("team"), teams)
        decision = "bat" if toss.group("dec").lower() == "bat" else "bowl"
        if winner:
            conn.execute(
                "UPDATE matches SET toss_winner_id = ?, toss_decision = ? "
                "WHERE match_id = ?", (winner, decision, match_id))

    v = payload.get("venueinfo") or {}
    if v.get("id"):
        digits = re.sub(r"\D", "", str(v.get("capacity") or ""))
        capacity = int(digits) if digits and int(digits) > 0 else None
        conn.execute(
            """INSERT INTO venues (cb_venue_id, venue_name, city, country, capacity)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(cb_venue_id) DO UPDATE SET
                   venue_name = excluded.venue_name,
                   city = excluded.city,
                   country = excluded.country,
                   capacity = COALESCE(excluded.capacity, venues.capacity)""",
            (v["id"], v.get("ground") or "Unknown", v.get("city"),
             v.get("country"), capacity))
        venue_id = conn.execute(
            "SELECT venue_id FROM venues WHERE cb_venue_id = ?",
            (v["id"],)).fetchone()[0]
        conn.execute("UPDATE matches SET venue_id = ? WHERE match_id = ?",
                     (venue_id, match_id))

    for key in ("team1", "team2"):
        t = payload.get(key) or {}
        if t.get("teamid") and t.get("countryname"):
            conn.execute("UPDATE teams SET country = ? WHERE cb_team_id = ?",
                         (t["countryname"], t["teamid"]))
    return True