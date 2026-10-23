
"""Cricbuzz LiveStats — Cricket Analytics Dashboard."""

import html
import streamlit as st

from utils.sidebar import render_sidebar
from api.cricbuzz_client import CricbuzzClient
from services.home_service import api_key_configured, get_home_stats


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Cricbuzz LiveStats | Cricket Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --navy: #071a38;
        --blue: #0878f9;
        --cyan: #38c7ff;
        --ink: #102344;
        --muted: #71829a;
        --border: #dce8f7;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f9ff, #edf4fc 60%, #f8fbff);
    }

    [data-testid="stHeader"] {
        background: rgba(245,249,255,.92);
    }

    .block-container {
        max-width: 1600px;
        padding: 1.2rem 1.35rem 2rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #061735, #0b2b54 65%, #041329);
    }

    /* Hide Streamlit's automatically generated page navigation (which labels
       the entry point "app"). The branded links below are the only navigation. */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    section[data-testid="stSidebar"] nav[aria-label="pages"],
    section[data-testid="stSidebar"] > div > div > div[data-testid="stSidebarNav"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        visibility: hidden !important;
        overflow: hidden !important;
    }

    /* Keep the custom sidebar links readable on the dark background. */
    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        margin: 4px 0;
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] a {
        display: flex !important;
        align-items: center;
        justify-content: flex-start !important;
        width: 100%;
        min-height: 42px;
        padding: 9px 12px !important;
        background: transparent !important;
        color: #e6f0ff !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        text-decoration: none !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] a *,
    [data-testid="stSidebar"] [data-testid="stPageLink"] a span,
    [data-testid="stSidebar"] [data-testid="stPageLink"] a p {
        color: #e6f0ff !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
        background: rgba(73, 151, 255, .18) !important;
        border-color: rgba(120, 183, 255, .25) !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption {
        color: #dce9ff !important;
    }

    .brand {
        padding: 10px 5px 18px;
    }

    .brand-title {
        color: white;
        font-size: 1.55rem;
        font-weight: 850;
        line-height: 1.1;
    }

    .brand-title span {
        color: var(--cyan);
    }

    .brand-caption {
        color: #a9c2e2;
        font-size: .72rem;
        margin-top: 10px;
        letter-spacing: .06em;
    }

    .hero {
        padding: 28px;
        border-radius: 20px;
        color: white;
        background:
            radial-gradient(ellipse at 80% 0%,
                rgba(44,184,255,.34), transparent 34%),
            radial-gradient(ellipse at 95% 100%,
                rgba(17,210,160,.2), transparent 34%),
            linear-gradient(110deg, #061735, #0c3b72 56%, #071b39);
        border: 1px solid rgba(255,255,255,.15);
        box-shadow: 0 12px 34px rgba(16,54,102,.14);
        margin-bottom: 1.2rem;
    }

    .hero-tag {
        display: inline-block;
        border: 1px solid rgba(88,207,255,.35);
        background: rgba(36,168,255,.15);
        color: #92e7ff;
        border-radius: 30px;
        padding: 6px 12px;
        font-size: .72rem;
        font-weight: 750;
    }

    .hero h1 {
        color: white !important;
        font-size: clamp(2rem, 4vw, 3.15rem) !important;
        line-height: 1.08;
        margin: .8rem 0 .6rem;
    }

    .hero h1 span {
        color: var(--cyan);
    }

    .hero p {
        color: #dcecff;
        max-width: 760px;
        line-height: 1.6;
        margin-bottom: 0;
    }

    .hero-features {
        color: #c7e5ff;
        font-size: .82rem;
        margin-top: 16px;
    }

    [data-testid="stMetric"] {
        background: rgba(255,255,255,.97);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 13px 15px;
        box-shadow: 0 5px 18px rgba(27,69,120,.045);
    }

    [data-testid="stMetricLabel"] {
        color: #60748f;
        font-weight: 650;
    }

    [data-testid="stMetricValue"] {
        color: #0a244a;
        font-weight: 850;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,.97);
        border: 1px solid #dce8f7 !important;
        border-radius: 15px !important;
        padding: .8rem 1rem !important;
        box-shadow: 0 5px 20px rgba(27,69,120,.04);
    }

    .section-title {
        color: var(--ink);
        font-size: 1.15rem;
        font-weight: 800;
    }

    .muted {
        color: var(--muted);
        font-size: .86rem;
        line-height: 1.55;
    }

    .live-pill {
        display: inline-block;
        background: #fff0f0;
        color: #d91f35;
        border: 1px solid #ffd1d6;
        border-radius: 7px;
        padding: 3px 8px;
        font-size: .7rem;
        font-weight: 800;
    }

    .team-name {
        color: #526780;
        font-size: .82rem;
        margin-top: 10px;
    }

    .score-value {
        color: #092c5c;
        font-size: 1.25rem;
        font-weight: 850;
    }

    .action-title {
        color: #102344;
        font-weight: 750;
        font-size: .94rem;
        margin-bottom: 4px;
    }

    .action-description {
        color: #71829a;
        font-size: .8rem;
        line-height: 1.5;
    }

    .status-card {
        background: #f2f7fd;
        border: 1px solid #e3edf9;
        border-radius: 10px;
        padding: 11px;
        color: #193456;
        font-size: .83rem;
    }

    .status-good {
        color: #12824b;
        font-weight: 750;
    }

    .stButton > button,
    [data-testid="stPageLink"] a {
        border-radius: 10px !important;
        font-weight: 650 !important;
    }

    /* Main-page links are button-like; sidebar links retain their dark theme. */
    [data-testid="stMain"] [data-testid="stPageLink"] a {
        background: #edf5ff;
        border: 1px solid #d7e7fb;
        padding: .55rem .65rem;
        width: 100%;
        justify-content: center;
        color: #102344 !important;
    }

    [data-testid="stMain"] [data-testid="stPageLink"] a:hover {
        background: #dcecff;
        border-color: #9ec8ff;
    }

    hr {
        border-color: #dce7f5;
    }

    @media (max-width: 800px) {
        .block-container {
            padding: .8rem .75rem 1.5rem;
        }
        .hero {
            padding: 22px 18px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# API HELPERS
# =========================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_live_matches():
    """Fetch and flatten live matches from Cricbuzz."""
    response = CricbuzzClient().live_matches()
    matches = []

    if not isinstance(response, dict):
        return matches

    for group in response.get("typeMatches", []):
        for series in group.get("seriesMatches", []):
            wrapper = series.get("seriesAdWrapper", {})
            matches.extend(wrapper.get("matches", []))

    if matches:
        return matches

    for key in ("matches", "matchList", "data"):
        value = response.get(key)
        if isinstance(value, list):
            return value

    return []


@st.cache_data(ttl=60, show_spinner=False)
def fetch_scorecard(match_id):
    """Fetch the scorecard for one match."""
    return CricbuzzClient().scorecard(int(match_id))


def safe_text(value, fallback="—"):
    """Escape text before inserting it into HTML."""
    if value is None or value == "":
        return fallback
    return html.escape(str(value))


def normalize_match(item):
    """Convert a Cricbuzz match response into display fields."""
    if not isinstance(item, dict):
        return {}

    match = item.get("match", item)
    if not isinstance(match, dict):
        match = {}

    info = match.get("matchInfo", match)
    if not isinstance(info, dict):
        info = {}

    team1 = info.get("team1") or {}
    team2 = info.get("team2") or {}
    score = match.get("matchScore") or {}

    def team_name(team, fallback):
        if not isinstance(team, dict):
            return fallback
        return (
            team.get("teamName")
            or team.get("name")
            or team.get("teamSName")
            or fallback
        )

    def get_innings(team_score):
        if not isinstance(team_score, dict):
            return {}
        return (
            team_score.get("inngs1")
            or team_score.get("inngs2")
            or {}
        )

    def format_score(team_score):
        innings = get_innings(team_score)
        if not innings:
            return "Score unavailable"

        runs = innings.get("runs", "—")
        wickets = innings.get("wickets", "—")
        overs = innings.get("overs")

        result = f"{runs}/{wickets}"
        if overs is not None and overs != "":
            result += f" ({overs} ov)"

        return result

    venue = info.get("venueInfo") or {}

    t1 = team_name(team1, "Team 1")
    t2 = team_name(team2, "Team 2")

    return {
        "id": info.get("matchId") or match.get("matchId"),
        "title": f"{t1} vs {t2}",
        "team1": t1,
        "team2": t2,
        "format": info.get("matchFormat", "CRICKET"),
        "description": info.get("matchDesc", ""),
        "series": info.get("seriesName", ""),
        "venue": venue.get("ground", ""),
        "status": info.get("status", "Match information"),
        "score1": format_score(score.get("team1Score")),
        "score2": format_score(score.get("team2Score")),
    }


# =========================================================
# SCORECARD
# =========================================================
def _key_lookup(source, names):
    """Find a dictionary key case-insensitively."""
    if not isinstance(source, dict):
        return None
    lookup = {str(key).lower(): key for key in source}
    for name in names:
        actual = lookup.get(str(name).lower())
        if actual is not None:
            return source[actual]
    return None


def _first_dict(source, keys):
    """Return the first non-empty dictionary under candidate keys."""
    if not isinstance(source, dict):
        return {}
    for key in keys:
        value = _key_lookup(source, [key])
        if isinstance(value, dict) and value:
            return value
    return {}


def _first_value(source, keys, default=None):
    """Read a field while tolerating different key casing."""
    if not isinstance(source, dict):
        return default
    for key in keys:
        value = _key_lookup(source, [key])
        if value is not None and value != "":
            return value
    return default


def _rows_from_api(value):
    """Convert list/dict player collections to a list of dictionaries."""
    if isinstance(value, dict):
        # Some API versions wrap rows inside a named collection.
        for key in ("data", "items", "players", "batsman", "batsmen", "bowler", "bowlers", "values"):
            nested = _key_lookup(value, [key])
            if isinstance(nested, (dict, list)):
                rows = _rows_from_api(nested)
                if rows:
                    return rows
        values = list(value.values())
    elif isinstance(value, list):
        values = value
    else:
        return []
    return [item for item in values if isinstance(item, dict)]


def _find_innings(data):
    """Find innings records across common Cricbuzz scorecard response shapes."""
    if not isinstance(data, dict):
        return []

    # Standard Cricbuzz scorecard responses use scoreCard.
    for key in ("scoreCard", "scorecard", "scoreCards", "innings", "inns"):
        value = _key_lookup(data, [key])
        if isinstance(value, list) and value:
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict) and value:
            # A single innings object or a map of innings objects.
            if any(
                _key_lookup(value, candidate) is not None
                for candidate in ("batTeamDetails", "batsmenData", "batsman", "batsmen", "bowlTeamDetails", "bowler", "bowlers")
            ):
                return [value]
            return [item for item in value.values() if isinstance(item, dict)]

    # Try common wrappers.
    for wrapper_key in ("data", "response", "result", "scorecardData"):
        wrapper = _key_lookup(data, [wrapper_key])
        if isinstance(wrapper, dict):
            found = _find_innings(wrapper)
            if found:
                return found

    # Last resort: recursively locate objects that look like an innings.
    found = []
    def walk(node):
        if isinstance(node, dict):
            has_batting = any(
                _key_lookup(node, [key]) is not None
                for key in ("batTeamDetails", "battingTeamDetails", "batsmenData", "batsman", "batsmen")
            )
            has_bowling = any(
                _key_lookup(node, [key]) is not None
                for key in ("bowlTeamDetails", "bowlingTeamDetails", "bowlersData", "bowler", "bowlers")
            )
            if has_batting or has_bowling:
                found.append(node)
                return
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)
    walk(data)
    return found


def render_scorecard(data):
    """Render scorecard tables while tolerating Cricbuzz response variations."""
    if not isinstance(data, dict) or not data:
        st.warning("Cricbuzz returned an empty scorecard response.")
        return

    innings_list = _find_innings(data)
    if not innings_list:
        st.warning(
            "Cricbuzz returned a response, but no innings records were recognised. "
            "The raw response is available below for diagnosis."
        )
        with st.expander("Inspect Cricbuzz scorecard response"):
            st.json(data)
        return

    tables_rendered = 0
    for index, inning in enumerate(innings_list, start=1):
        batting_details = _first_dict(
            inning,
            ["batTeamDetails", "battingTeamDetails", "batting", "batTeam"],
        )
        bowling_details = _first_dict(
            inning,
            ["bowlTeamDetails", "bowlingTeamDetails", "bowling", "bowlTeam"],
        )

        # If the team details are nested, search one level deeper.
        if not batting_details:
            for value in inning.values():
                if isinstance(value, dict):
                    batting_details = _first_dict(
                        value,
                        ["batTeamDetails", "battingTeamDetails", "batting", "batTeam"],
                    )
                    if batting_details:
                        break
        if not bowling_details:
            for value in inning.values():
                if isinstance(value, dict):
                    bowling_details = _first_dict(
                        value,
                        ["bowlTeamDetails", "bowlingTeamDetails", "bowling", "bowlTeam"],
                    )
                    if bowling_details:
                        break

        # Some payloads put batsmen/bowlers directly on the innings object.
        batsmen = _first_value(
            batting_details,
            ["batsmenData", "batsmanData", "batsman", "batsmen", "batters", "battingStats"],
        )
        if batsmen is None:
            batsmen = _first_value(
                inning, ["batsmenData", "batsmanData", "batsman", "batsmen", "batters"]
            )

        bowlers = _first_value(
            bowling_details,
            ["bowlersData", "bowlerData", "bowler", "bowlers", "bowlingStats"],
        )
        if bowlers is None:
            bowlers = _first_value(
                inning, ["bowlersData", "bowlerData", "bowler", "bowlers"]
            )

        team_name = (
            _first_value(
                batting_details,
                ["batTeamName", "batteamname", "batTeam", "teamName", "name", "batTeamShortName"],
            )
            or _first_value(inning, ["batTeamName", "batteamname", "batTeam", "teamName", "name"])
            or f"Innings {index}"
        )
        st.markdown(f"#### 🏏 {safe_text(team_name)}")

        # Display innings totals when supplied by the API.
        score_details = _first_dict(
            inning, ["scoreDetails", "score", "inngs1", "inningsScore", "scoreInfo", "batTeamScore"]
        )
        runs = _first_value(score_details, ["runs", "score", "teamScore", "runsScored"])
        wickets = _first_value(score_details, ["wickets", "wkts", "wicketsLost"])
        overs = _first_value(score_details, ["overs", "over", "oversPlayed"])
        if runs is not None:
            total = str(runs)
            if wickets is not None:
                total += f"/{wickets}"
            if overs is not None:
                total += f" ({overs} ov)"
            st.caption(f"Total: {total}")

        batting_rows = []
        for batter in _rows_from_api(batsmen):
            batting_rows.append({
                "Batter": _first_value(
                    batter, ["batName", "batsmanName", "batsmanname", "name", "playerName", "fullName"], "—"
                ),
                "Dismissal": _first_value(
                    batter, ["outDesc", "outdesc", "dismissal", "outDescription"], "—"
                ),
                "Runs": _first_value(batter, ["runs", "run"], 0),
                "Balls": _first_value(batter, ["balls", "ballsFaced"], 0),
                "4s": _first_value(batter, ["fours", "four"], 0),
                "6s": _first_value(batter, ["sixes", "six"], 0),
                "Strike Rate": _first_value(batter, ["strikeRate", "strkrate", "strikerate", "sr"], "—"),
            })
        if batting_rows:
            st.markdown("**Batting**")
            st.dataframe(batting_rows, use_container_width=True, hide_index=True)
            tables_rendered += 1
        else:
            st.info("Batting details are not available in this innings response.")

        bowling_rows = []
        for bowler in _rows_from_api(bowlers):
            bowling_rows.append({
                "Bowler": _first_value(
                    bowler, ["bowlName", "bowlerName", "bowlername", "name", "playerName", "fullName"], "—"
                ),
                "Overs": _first_value(bowler, ["overs", "over", "oversPlayed"], "—"),
                "Maidens": _first_value(bowler, ["maidens", "maiden"], 0),
                "Runs": _first_value(bowler, ["runs", "conceded"], 0),
                "Wickets": _first_value(bowler, ["wickets", "wkts", "wicketsLost"], 0),
                "Economy": _first_value(bowler, ["economy", "econ", "econrate"], "—"),
            })
        if bowling_rows:
            st.markdown("**Bowling**")
            st.dataframe(bowling_rows, use_container_width=True, hide_index=True)
            tables_rendered += 1
        else:
            st.caption("Bowling figures are not available in this innings response.")

    if tables_rendered == 0:
        with st.expander("Inspect Cricbuzz scorecard response"):
            st.json(data)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
render_sidebar()


# =========================================================
# HERO BANNER
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-tag">● CRICKET ANALYTICS WORKSPACE</div>
        <h1>Cricbuzz <span>LiveStats</span></h1>
        <p>
            Real-time cricket insights and SQL-based analytics.
            Explore live match scorecards, player statistics and data trends
            in one place.
        </p>
        <div class="hero-features">
            📡 Live Matches &nbsp; • &nbsp;
            📊 Player Statistics &nbsp; • &nbsp;
            📈 Analytics &nbsp; • &nbsp;
            🗄️ Data Management
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATABASE METRICS
# =========================================================
try:
    stats = get_home_stats() or {}
    database_connected = True
except Exception as exc:
    stats = {}
    database_connected = False
    st.warning(f"Could not load database statistics: {exc}")

stats_lookup = {
    str(key).strip().lower(): value
    for key, value in stats.items()
}

metric_columns = st.columns(4, gap="medium")

for column, label, icon in zip(
    metric_columns,
    ["Players", "Matches", "Venues", "Series"],
    ["👥", "🏏", "🏟️", "🏆"],
):
    value = stats_lookup.get(label.lower(), 0)

    try:
        value = f"{int(value):,}"
    except (TypeError, ValueError):
        value = str(value)

    column.metric(f"{icon} {label}", value)

st.write("")


# =========================================================
# DASHBOARD LAYOUT
# =========================================================
main_column, side_column = st.columns([2.05, 1], gap="medium")


# =========================================================
# LEFT COLUMN
# =========================================================
with main_column:

    # -----------------------------------------------------
    # LIVE MATCHES
    # -----------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-title">🔴 Live Matches</div>',
            unsafe_allow_html=True,
        )
        

        refresh_col, info_col = st.columns([1, 2])

        with refresh_col:
            if st.button(
                "🔄 Refresh matches",
                use_container_width=True,
            ):
                fetch_live_matches.clear()
                fetch_scorecard.clear()
                st.rerun()

        with info_col:
            st.caption("Match data is cached for 60 seconds.")

        try:
            raw_matches = fetch_live_matches()
            matches = [
                normalize_match(item)
                for item in raw_matches
            ]
            matches = [
                match for match in matches
                if match.get("id") is not None
            ]
        except Exception as exc:
            matches = []
            st.error(f"Could not fetch live matches: {exc}")

        if not matches:
            st.info(
                "No live matches are available right now, or the API "
                "request failed. Check your API quota and Settings page."
            )
        else:
            shown_matches = matches[:2]
            match_columns = st.columns(
                len(shown_matches),
                gap="medium",
            )

            for index, match in enumerate(shown_matches):
                with match_columns[index]:
                    # Use Streamlit components for the card content.
                    # This avoids HTML tags appearing as literal text.
                    with st.container(border=True):
                        st.markdown(f"**{match['title']}**")
                        st.caption(
                            f"{match['format']} · "
                            f"{match['description'] or 'Match'}"
                        )

                        st.markdown(
                            '<span class="live-pill">● LIVE / MATCH</span>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f'<div class="team-name">'
                            f'{safe_text(match["team1"])}</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f'<div class="score-value">'
                            f'{safe_text(match["score1"])}</div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f'<div class="team-name">'
                            f'{safe_text(match["team2"])}</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f'<div class="score-value">'
                            f'{safe_text(match["score2"])}</div>',
                            unsafe_allow_html=True,
                        )

                        st.caption(match["status"] or "Match information")

                        if match.get("venue"):
                            st.caption(f"🏟️ {match['venue']}")

                        if st.button(
                            "View this scorecard →",
                            key=f"select_match_{match['id']}",
                            use_container_width=True,
                        ):
                            st.session_state[
                                "selected_dashboard_match"
                            ] = str(match["id"])
                            st.session_state[
                                "scorecard_requested"
                            ] = True

            # Show the scorecard only after a user clicks a match card button.
            # This keeps the dashboard free of the old dropdown selector.
            if st.session_state.get("scorecard_requested", False):
                selected_id = st.session_state.get("selected_dashboard_match")
                selected_match = next(
                    (m for m in matches if str(m.get("id")) == str(selected_id)),
                    None,
                )

                if selected_match:
                    st.divider()
                    st.markdown(
                        f"### 📋 Scorecard: {safe_text(selected_match['title'])}"
                    )
                    try:
                        with st.spinner("Loading scorecard from Cricbuzz…"):
                            scorecard_data = fetch_scorecard(selected_id)
                        render_scorecard(scorecard_data)
                    except Exception as exc:
                        st.error(f"Could not load the scorecard: {exc}")
                        st.caption(
                            "Check your RapidAPI quota and try again when it is available."
                        )

        st.write("")
        

    # -----------------------------------------------------
    # PLAYER SPOTLIGHT IMAGE
    # -----------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-title">🏏 Cricket Player Spotlight</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="muted">'
            'Cricket photography to bring the dashboard to life.'
            '</div>',
            unsafe_allow_html=True,
        )
        try:
            st.image(
                "https://images.unsplash.com/photo-1531415074968-036ba1b575da"
                "?auto=format&fit=crop&w=1400&q=85",
                use_container_width=True,
            )
        except Exception:
            st.caption("Cricket player image is currently unavailable.")

    st.write("")

    # -----------------------------------------------------
    # STADIUM IMAGE
    # -----------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-title">🏟️ The Cricket Experience</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="muted">'
            'A stadium view for the atmosphere of match day.'
            '</div>',
            unsafe_allow_html=True,
        )
        try:
            st.image(
                "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e"
                "?auto=format&fit=crop&w=1400&q=85",
                use_container_width=True,
            )
        except Exception:
            st.caption("Stadium image is currently unavailable.")


# =========================================================
# RIGHT COLUMN
# =========================================================
with side_column:

    # -----------------------------------------------------
    # QUICK ACTIONS
    # -----------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-title">⚡ Quick Actions</div>',
            unsafe_allow_html=True,
        )

        actions = [
            (
                "📡 Live Matches",
                "Ongoing matches and scorecards.",
                "pages/1_Live_Matches.py",
                "Open Live Matches →",
                "📡",
            ),
            (
                "📊 Top Stats",
                "Player leaderboards and performance.",
                "pages/2_Top_Stats.py",
                "Explore Top Stats →",
                "📊",
            ),
            (
                "🔎 SQL Queries",
                "Explore the project's analytical queries.",
                "pages/3_SQL_Queries.py",
                "Open SQL Analytics →",
                "🔎",
            ),
            (
                "🛠️ CRUD Operations",
                "Manage player records in your database.",
                "pages/4_CRUD_Operations.py",
                "Manage Players →",
                "🛠️",
            ),
        ]

        for title, description, page, button_label, icon in actions:
            with st.container(border=True):
                st.markdown(
                    f'<div class="action-title">'
                    f'{safe_text(title)}</div>'
                    f'<div class="action-description">'
                    f'{safe_text(description)}</div>',
                    unsafe_allow_html=True,
                )
                st.page_link(
                    page,
                    label=button_label,
                    icon=icon,
                    use_container_width=True,
                )

    st.write("")

    # -----------------------------------------------------
    # SYSTEM STATUS
    # -----------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-title">🟢 System Status</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="muted">'
            'Status of your local database and API configuration.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.write("")

        if database_connected:
            st.markdown(
                """
                <div class="status-card">
                    🗄️ Database<br>
                    <span class="status-good">Connected</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.error("Database unavailable")

        st.write("")

        try:
            configured = api_key_configured()
        except Exception:
            configured = False

        if configured:
            st.markdown(
                """
                <div class="status-card">
                    🔌 Cricbuzz API<br>
                    <span class="status-good">Key configured</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning("Cricbuzz API key is not configured.")

        st.write("")
        st.page_link(
            "pages/5_Settings.py",
            label="Open Settings →",
            icon="⚙️",
            use_container_width=True,
        )

    st.write("")

    # -----------------------------------------------------
    # CHARTS AND TRENDS
    # -----------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-title">📈 Charts & Trends</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="muted">'
            'Visualise top scorers, player form, team wins and batting '
            'trends using the data available in your project.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.write("")
        st.page_link(
            "pages/6_Charts.py",
            label="View Charts →",
            icon="📈",
            use_container_width=True,
        )


# =========================================================
# FOOTER
# =========================================================
st.write("")
st.divider()

left_footer, right_footer = st.columns(2)

with left_footer:
    st.caption("🏏 Cricbuzz LiveStats · Cricket data, clearer insights")

with right_footer:
    st.markdown(
        """
        <div style="text-align:right;color:#8293aa;font-size:.8rem">
            Python · Streamlit · SQLite · Cricbuzz API
        </div>
        """,
        unsafe_allow_html=True,
    )
