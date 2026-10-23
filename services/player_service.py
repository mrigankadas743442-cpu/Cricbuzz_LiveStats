
"""Top-player data: Cricbuzz API first, local database fallback."""

import pandas as pd

from api.cricbuzz_client import CricbuzzClient
from database.connection import get_connection


FORMAT_IDS = {
    "Test": 1,
    "ODI": 2,
    "T20I": 3,
}

CATEGORIES = {
    "Most Runs": "mostRuns",
    "Highest Score": "highestScore",
    "Best Batting Average": "highestAvg",
    "Best Batting Strike Rate": "highestSr",
    "Most Hundreds": "mostHundreds",
    "Most Fifties": "mostFifties",
    "Most Fours": "mostFours",
    "Most Sixes": "mostSixes",
    "Most Nineties": "mostNineties",
    "Most Wickets": "mostWickets",
    "Best Bowling Average": "lowestAvg",
    "Best Bowling": "bestBowlingInnings",
    "Most 5-Wicket Hauls": "mostFiveWickets",
    "Best Economy": "lowestEcon",
    "Best Bowling Strike Rate": "lowestSr",
}

# Only columns available in the local player_career_stats table.
_FALLBACK = {
    "Most Runs": ("runs", "DESC"),
    "Highest Score": ("highest_score", "DESC"),
    "Best Batting Average": ("batting_avg", "DESC"),
    "Best Batting Strike Rate": ("strike_rate", "DESC"),
    "Most Hundreds": ("centuries", "DESC"),
    "Most Wickets": ("wickets", "DESC"),
    "Best Bowling Average": ("bowling_avg", "ASC"),
    "Best Economy": ("economy", "ASC"),
}

# Cricbuzz abbreviations -> readable column names.
_HEADER_NAMES = {
    "M": "Matches",
    "Mat": "Matches",
    "I": "Innings",
    "R": "Runs",
    "HS": "Highest Score",
    "SR": "Strike Rate",
    "Avg": "Batting Average",
    "50s": "Fifties",
    "100s": "Centuries",
    "4s": "Fours",
    "6s": "Sixes",
    "90s": "Nineties",
    "O": "Overs",
    "W": "Wickets",
    "Eco": "Economy",
    "Econ": "Economy",
    "BBI": "Best Bowling",
    "BBM": "Best Match Bowling",
    "Balls": "Balls Faced",
    "Vs": "Opponent",
    "Country": "Country",
    "Team": "Team",
    "Runs": "Runs",
    "Avg": "Average",
    "SR": "Strike Rate",
    "5W": "Five-Wicket Hauls",
    "10W": "Ten-Wicket Hauls",
    "BF": "Balls Faced",
    "Mdns": "Maidens",
    "Inn": "Innings",
    "Econ": "Economy",
}

# Category-specific labels are used when an API response doesn't
# provide a recognizable header for a statistic.
_CATEGORY_STAT_COLUMNS = {
    "Most Runs": ["Matches", "Innings", "Runs", "Average"],
    "Highest Score": [
        "Highest Score", "Balls Faced", "Strike Rate", "Opponent"
    ],
    "Best Batting Average": [
        "Matches", "Innings", "Runs", "Batting Average"
    ],
    "Best Batting Strike Rate": [
        "Matches", "Innings", "Runs", "Strike Rate"
    ],
    "Most Hundreds": ["Matches", "Innings", "Runs", "Centuries"],
    "Most Fifties": ["Matches", "Innings", "Runs", "Fifties"],
    "Most Fours": ["Matches", "Innings", "Runs", "Fours"],
    "Most Sixes": ["Matches", "Innings", "Runs", "Sixes"],
    "Most Nineties": ["Matches", "Innings", "Runs", "Nineties"],
    "Most Wickets": ["Matches", "Overs", "Wickets", "Economy"],
    "Best Bowling Average": [
        "Matches", "Overs", "Wickets", "Bowling Average"
    ],
    "Best Bowling": ["Country", "Best Bowling"],
    "Most 5-Wicket Hauls": [
        "Matches", "Overs", "Wickets", "Five-Wicket Hauls"
    ],
    "Best Economy": ["Matches", "Overs", "Wickets", "Economy"],
    "Best Bowling Strike Rate": [
        "Matches", "Overs", "Wickets", "Bowling Strike Rate"
    ],
}


def _friendly_header(header: str) -> str:
    """Convert a Cricbuzz abbreviation to a readable label."""
    return _HEADER_NAMES.get(header, header.strip() or "Statistic")


def parse_topstats(
    payload: dict,
    category: str = "Most Runs",
) -> pd.DataFrame:
    """Parse Cricbuzz leaderboard responses into readable columns."""

    if not isinstance(payload, dict):
        return pd.DataFrame()

    headers = payload.get("headers") or []
    values = payload.get("values") or []

    rows = []
    for item in values:
        row = item.get("values") if isinstance(item, dict) else item
        if isinstance(row, (list, tuple)) and row:
            rows.append(list(row))

    if not rows:
        return pd.DataFrame()

    # Normalize row lengths.
    width = max(len(row) for row in rows)
    rows = [
        row + [None] * (width - len(row))
        for row in rows
    ]

    # Cricbuzz normally returns the player ID and player name first.
    if width >= 2:
        columns = ["Player ID", "Player"]

        # The first header identifies the entity type ("Batter" or
        # "Bowler"); the remaining headers describe the statistics.
        stat_headers = headers[1:] if len(headers) > 1 else []
        stat_names = [_friendly_header(str(h)) for h in stat_headers]

        # Fill missing names with category-specific labels.
        fallback_names = _CATEGORY_STAT_COLUMNS.get(category, [])
        while len(stat_names) < width - 2:
            position = len(stat_names)
            if position < len(fallback_names):
                stat_names.append(fallback_names[position])
            else:
                stat_names.append(f"Statistic {position + 1}")

        columns.extend(stat_names[:width - 2])
    else:
        columns = [f"Field {i + 1}" for i in range(width)]

    # Ensure the number of column names matches the row width.
    if len(columns) < width:
        columns.extend(
            f"Statistic {i + 1}"
            for i in range(len(columns), width)
        )
    columns = columns[:width]

    df = pd.DataFrame(rows, columns=columns)

    # Preserve player, opponent, country, and team names as text.
    text_columns = {"Player", "Opponent", "Country", "Team"}

    for column in df.columns:
        if column not in text_columns:
            converted = pd.to_numeric(df[column], errors="coerce")
            if converted.notna().any():
                df[column] = converted

    return df.dropna(axis=1, how="all")


def fetch_top_stats_api(
    category: str,
    fmt: str,
) -> pd.DataFrame:
    """Fetch and parse a leaderboard from Cricbuzz."""

    if category not in CATEGORIES:
        raise ValueError(f"Unsupported category: {category}")

    if fmt not in FORMAT_IDS:
        raise ValueError(f"Unsupported match format: {fmt}")

    payload = CricbuzzClient().top_stats(
        CATEGORIES[category],
        FORMAT_IDS[fmt],
    )

    return parse_topstats(payload, category)


def fetch_top_stats_db(
    category: str,
    fmt: str,
    limit: int = 10,
) -> pd.DataFrame:
    """Fetch local database data for supported categories."""

    if fmt not in FORMAT_IDS:
        raise ValueError(f"Unsupported match format: {fmt}")

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    fallback = _FALLBACK.get(category)
    if fallback is None:
        return pd.DataFrame()

    column, direction = fallback

    sql = f"""
        SELECT
            p.full_name AS Player,
            s.{column} AS "{column}"
        FROM player_career_stats AS s
        JOIN players AS p
            ON p.player_id = s.player_id
        WHERE s.format = ?
          AND s.{column} IS NOT NULL
        ORDER BY s.{column} {direction}
        LIMIT ?
    """

    with get_connection() as connection:
        return pd.read_sql_query(
            sql,
            connection,
            params=(fmt, limit),
        )
