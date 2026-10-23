from services.match_service import _score_text, parse_matches, parse_scorecard


def test_score_text_yet_to_bat():
    assert _score_text(None) == "Yet to bat"
    assert _score_text({}) == "Yet to bat"


def test_score_text_one_and_two_innings():
    one = {"inngs1": {"runs": 210, "wickets": 3, "overs": 45.2}}
    assert _score_text(one) == "210/3 (45.2 ov)"
    two = {"inngs1": {"runs": 300, "wickets": 10, "overs": 90},
           "inngs2": {"runs": 50, "wickets": 1, "overs": 12}}
    assert _score_text(two) == "300/10 (90 ov) & 50/1 (12 ov)"


def test_parse_matches_flattens_nested_payload():
    payload = {"typeMatches": [{"seriesMatches": [{"seriesAdWrapper": {
        "seriesName": "Test Series",
        "matches": [{"matchInfo": {
            "matchId": 1, "matchDesc": "1st Test", "matchFormat": "TEST",
            "state": "Complete", "status": "India won",
            "team1": {"teamName": "India"}, "team2": {"teamName": "Australia"},
            "venueInfo": {"ground": "Eden Gardens", "city": "Kolkata"}}}]}}]}]}
    [m] = parse_matches(payload)
    assert (m["match_id"], m["team1"], m["team2"]) == (1, "India", "Australia")
    assert m["venue"] == "Eden Gardens, Kolkata"


def test_parse_matches_skips_entries_without_id():
    payload = {"typeMatches": [{"seriesMatches": [{"seriesAdWrapper": {
        "matches": [{"matchInfo": {"matchDesc": "no id"}}]}}]}]}
    assert parse_matches(payload) == []


def test_parse_scorecard_real_field_names_and_did_not_bat():
    payload = {"scorecard": [{
        "batteamname": "India", "score": 118, "wickets": 5, "overs": 7.4,
        "extras": {"total": 13},
        "batsman": [{"name": "A", "runs": 16, "balls": 7, "outdec": "b X"},
                    {"name": "B", "runs": 0, "balls": 0, "outdec": ""}],
        "bowler": [{"name": "C", "overs": "2", "runs": 34, "wickets": 2}]}]}
    [inn] = parse_scorecard(payload)
    assert inn["title"] == "Innings 1: India"
    assert inn["total"] == "118/5 (7.4 ov)"
    assert inn["extras"] == 13
    assert [b["Batter"] for b in inn["batting"]] == ["A"]
    assert inn["bowling"][0]["Bowler"] == "C"


def test_parse_scorecard_empty_payload():
    assert parse_scorecard({}) == []