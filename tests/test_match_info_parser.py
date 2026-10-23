from services.match_info_parser import parse_result

TEAMS = [(1, "India"), (2, "West Indies")]


def test_won_by_wickets():
    assert parse_result("India won by 5 wkts", TEAMS) == (1, 5, "wickets")


def test_won_by_runs():
    assert parse_result("West Indies won by 12 runs", TEAMS) == (2, 12, "runs")


def test_won_by_innings_and_runs():
    assert parse_result("India won by an innings and 20 runs", TEAMS) == (1, 20, "runs")


def test_draw_and_tie():
    assert parse_result("Match drawn", TEAMS) == (None, None, "draw")
    assert parse_result("Match tied", TEAMS) == (None, None, "tie")


def test_no_result_is_understood_but_has_no_winner():
    assert parse_result("No result", TEAMS) == (None, None, None)


def test_forfeit_gives_win_to_the_other_team():
    teams = [(1, "Arunachal Pradesh"), (2, "Mizoram")]
    status = "Arunachal Pradesh are deemed to have forfeited the match"
    assert parse_result(status, teams) == (2, None, None)


def test_unknown_text_returns_none():
    assert parse_result("Day 3: Stumps", TEAMS) is None
    assert parse_result("", TEAMS) is None
    assert parse_result(None, TEAMS) is None


def test_unknown_team_returns_none():
    assert parse_result("Mars won by 5 runs", TEAMS) is None

def test_extra_spaces_in_team_name_still_match():
    teams = [(1, "North West - Eastvaal Renault Dragons"), (2, "Other")]
    status = "North West  -  Eastvaal Renault Dragons won by 5 wkts"
    assert parse_result(status, teams) == (1, 5, "wickets")