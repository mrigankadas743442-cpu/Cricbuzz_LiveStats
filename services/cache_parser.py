"""Turn cached scorecard responses into innings / batting / bowling rows.

Works on a plain sqlite3 connection, so it never touches the API.
"""
NOT_OUT = {"not out", "batting", "retired hurt", "absent hurt"}


def _float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _player_id(conn, cb_id, name, country):
    conn.execute(
        """INSERT INTO players (cb_player_id, full_name, country)
           VALUES (?, ?, ?) ON CONFLICT(cb_player_id) DO NOTHING""",
        (cb_id, name, country))
    return conn.execute(
        "SELECT player_id FROM players WHERE cb_player_id = ?",
        (cb_id,)).fetchone()[0]


def parse_scorecard(conn, cb_match_id: int, payload: dict) -> int:
    """Save every innings in one scorecard payload. Returns innings saved.

    The match must already exist in `matches` (run the match-list ingest
    first), because we need its two team IDs.
    """
    match = conn.execute(
        "SELECT match_id, team1_id, team2_id FROM matches WHERE cb_match_id = ?",
        (cb_match_id,)).fetchone()
    if match is None:
        return 0
    match_id, t1, t2 = match[0], match[1], match[2]
    names = {r[0]: r[1] for r in conn.execute(
        "SELECT team_id, team_name FROM teams WHERE team_id IN (?, ?)", (t1, t2))}

    saved = 0
    for innings_no, inn in enumerate(payload.get("scorecard") or [], start=1):
        if innings_no > 4:
            break
        bat_team = next((tid for tid, n in names.items()
                         if n == inn.get("batteamname")), None)
        if bat_team is None:
            continue
        bowl_team = t2 if bat_team == t1 else t1

        conn.execute(
            """INSERT INTO innings
                   (match_id, innings_no, batting_team_id, total_runs, wickets, overs)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(match_id, innings_no) DO UPDATE SET
                   batting_team_id = excluded.batting_team_id,
                   total_runs = excluded.total_runs,
                   wickets = excluded.wickets,
                   overs = excluded.overs""",
            (match_id, innings_no, bat_team, _int(inn.get("score")),
             min(_int(inn.get("wickets")), 10), _float(inn.get("overs"))))
        innings_id = conn.execute(
            "SELECT innings_id FROM innings WHERE match_id = ? AND innings_no = ?",
            (match_id, innings_no)).fetchone()[0]
        conn.execute("DELETE FROM batting_scorecard WHERE innings_id = ?", (innings_id,))
        conn.execute("DELETE FROM bowling_scorecard WHERE innings_id = ?", (innings_id,))

        for pos, b in enumerate(inn.get("batsman") or [], start=1):
            outdec = (b.get("outdec") or "").strip()
            if not outdec or pos > 11 or not b.get("id") or not b.get("name"):
                continue  # did not bat
            pid = _player_id(conn, b["id"], b["name"], names[bat_team])
            conn.execute(
                """INSERT OR REPLACE INTO batting_scorecard
                       (innings_id, player_id, batting_position, runs, balls,
                        fours, sixes, strike_rate, is_out)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (innings_id, pid, pos, _int(b.get("runs")), _int(b.get("balls")),
                 _int(b.get("fours")), _int(b.get("sixes")),
                 _float(b.get("strkrate")),
                 0 if outdec.lower() in NOT_OUT else 1))

        for w in inn.get("bowler") or []:
            if not w.get("id") or not w.get("name"):
                continue
            pid = _player_id(conn, w["id"], w["name"], names[bowl_team])
            conn.execute(
                """INSERT OR REPLACE INTO bowling_scorecard
                       (innings_id, player_id, overs, maidens, runs_conceded,
                        wickets, economy)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (innings_id, pid, _float(w.get("overs"), 0.0),
                 _int(w.get("maidens")), _int(w.get("runs")),
                 min(_int(w.get("wickets")), 10), _float(w.get("economy"))))
        saved += 1
    return saved