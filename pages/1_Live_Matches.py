
"""Live Matches — Cricbuzz LiveStats."""

import html

import pandas as pd
import streamlit as st

from api.cricbuzz_client import CricbuzzAPIError
from services import match_service
from utils.ui import friendly_errors
from utils.sidebar import render_sidebar

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Live Matches | Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
)


# =========================================================
# BLUE DASHBOARD + NAVY SIDEBAR THEME
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --navy: #071a38;
        --navy-light: #103a70;
        --blue: #0878f9;
        --cyan: #38c7ff;
        --ink: #102344;
        --muted: #71829a;
        --border: #dce8f7;
    }

    /* Main page background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(
            135deg,
            #f5f9ff 0%,
            #edf4fc 55%,
            #f8fbff 100%
        );
    }

    [data-testid="stHeader"] {
        background: rgba(245, 249, 255, 0.94);
    }

    .block-container {
        max-width: 1500px;
        padding: 1.5rem 1.6rem 2.5rem;
    }

    /* =====================================================
       NAVY SIDEBAR
       ===================================================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #061735 0%,
            #0b2b54 58%,
            #041329 100%
        ) !important;
        border-right: 1px solid rgba(75, 160, 255, 0.18);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }

    /* Sidebar text */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] a {
        color: #e5efff;
    }

    /* Streamlit multipage navigation */
    [data-testid="stSidebarNav"] {
        padding-top: 0.35rem;
    }

    [data-testid="stSidebarNav"] a {
        color: #dce9ff !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        margin: 3px 8px !important;
        padding: 10px 12px !important;
        transition: all 0.18s ease;
    }

    [data-testid="stSidebarNav"] a:hover {
        background: rgba(35, 119, 235, 0.22) !important;
        border-color: rgba(79, 166, 255, 0.35) !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(
            100deg,
            #0878f9,
            #075acb
        ) !important;
        color: #ffffff !important;
        border-color: #258cff !important;
        font-weight: 750 !important;
        box-shadow: 0 5px 15px rgba(0, 89, 220, 0.22);
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(195, 219, 255, 0.15) !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #9bb6d9 !important;
    }

    [data-testid="stSidebar"] button {
        color: #dce9ff !important;
    }

    /* Sidebar brand */
    .sidebar-brand {
        padding: 12px 5px 20px;
        margin: 0 8px 18px;
        border-bottom: 1px solid rgba(195, 219, 255, 0.15);
    }

    .sidebar-brand .brand-icon {
        font-size: 2.35rem;
        line-height: 1.2;
        margin-bottom: 8px;
    }

    .sidebar-brand .brand-name {
        color: #ffffff;
        font-size: 1.65rem;
        font-weight: 850;
        line-height: 1.12;
    }

    .sidebar-brand .brand-name span {
        color: #38c7ff !important;
    }

    .sidebar-brand .brand-caption {
        color: #9bb6d9 !important;
        font-size: .7rem;
        letter-spacing: .08em;
        margin-top: 10px;
    }

    /* =====================================================
       LIVE MATCHES HERO
       ===================================================== */
    .live-hero {
        position: relative;
        overflow: hidden;
        padding: 28px 30px;
        margin-bottom: 22px;
        border-radius: 22px;
        color: white;
        background:
            radial-gradient(
                circle at 90% 10%,
                rgba(56, 199, 255, .35),
                transparent 32%
            ),
            linear-gradient(
                115deg,
                #061735,
                #0d3b75 62%,
                #0878a9
            );
        box-shadow: 0 12px 32px rgba(10, 48, 100, .16);
    }

    .live-hero .eyebrow {
        display: inline-block;
        color: #a6edff;
        background: rgba(56, 199, 255, .13);
        border: 1px solid rgba(106, 220, 255, .32);
        border-radius: 25px;
        padding: 6px 12px;
        font-size: .74rem;
        font-weight: 800;
        letter-spacing: .07em;
    }

    .live-hero h1 {
        color: white !important;
        font-size: clamp(2rem, 4vw, 3rem) !important;
        line-height: 1.15;
        margin: 16px 0 8px;
    }

    .live-hero h1 span {
        color: var(--cyan);
    }

    .live-hero p {
        color: #d8eaff;
        line-height: 1.65;
        margin: 0;
        max-width: 800px;
    }

    .live-hero .hero-art {
        position: absolute;
        right: 30px;
        top: 25px;
        font-size: 5rem;
        opacity: .24;
        transform: rotate(-12deg);
        pointer-events: none;
    }

    /* Section headings */
    .section-heading {
        color: var(--ink);
        font-size: 1.2rem;
        font-weight: 850;
        margin-bottom: 4px;
    }

    .section-description {
        color: var(--muted);
        line-height: 1.6;
        margin-bottom: 12px;
        font-size: .9rem;
    }

    /* Match labels */
    .match-label {
        display: inline-block;
        color: #0878f9;
        background: #e7f2ff;
        border: 1px solid #d0e5ff;
        border-radius: 7px;
        padding: 4px 9px;
        font-size: .72rem;
        font-weight: 800;
        margin: 5px 0 10px;
    }

    .match-status {
        border-left: 3px solid #0878f9;
        background: #f0f6ff;
        color: #345575;
        padding: 10px 12px;
        border-radius: 0 8px 8px 0;
        font-size: .84rem;
        line-height: 1.5;
        margin: 12px 0;
    }

    /* Scorecard banner */
    .scorecard-banner {
        background: linear-gradient(110deg, #071a38, #104782);
        color: white;
        padding: 20px 22px;
        border-radius: 15px;
        margin: 20px 0 16px;
    }

    .scorecard-banner h3 {
        color: white !important;
        margin: 0 0 5px;
    }

    .scorecard-banner p {
        color: #c9e1ff;
        margin: 0;
        font-size: .88rem;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f4f8ff);
        border: 1px solid #dce8f7;
        border-radius: 13px;
        padding: 12px 14px;
        box-shadow: 0 4px 14px rgba(17, 59, 110, .045);
    }

    [data-testid="stMetricLabel"] {
        color: #627895;
        font-weight: 700;
    }

    [data-testid="stMetricValue"] {
        color: #0a2d60;
        font-weight: 850;
    }

    /* Bordered containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, .96);
        border: 1px solid #d8e6f7 !important;
        border-radius: 16px !important;
        padding: 12px 15px !important;
        box-shadow: 0 5px 20px rgba(25, 66, 117, .045);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 42px;
        transition: all .15s ease;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(100deg, #0878f9, #075dd7);
        border: 1px solid #0878f9;
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: #075acb;
        border-color: #075acb;
        color: white;
    }

    /* Controls and tables */
    [data-testid="stRadio"] label {
        font-weight: 600;
    }

    [data-testid="stSelectbox"] > div > div {
        border-radius: 10px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #dce8f7;
        border-radius: 10px;
        overflow: hidden;
    }

    div[data-baseweb="tab-list"] {
        gap: 8px;
    }

    button[data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
    }

    hr {
        border-color: #dce8f7;
    }

    /* Responsive layout */
    @media (max-width: 700px) {
        .block-container {
            padding: 1rem .7rem 2rem;
        }

        .live-hero {
            padding: 22px 18px;
        }

        .live-hero .hero-art {
            right: 12px;
            font-size: 3rem;
        }

        .sidebar-brand .brand-name {
            font-size: 1.45rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR BRANDING
# =========================================================

render_sidebar()

# =========================================================
# CACHED DATA LOADERS
# =========================================================
@st.cache_data(ttl=60, show_spinner=False)
def load_matches(kind: str):
    """Load live or recent matches from the match service."""
    return match_service.fetch_matches(kind)


@st.cache_data(ttl=300, show_spinner=False)
def load_scorecard(match_id: int, complete: bool):
    """Load scorecard innings for a match."""
    return match_service.fetch_scorecard(match_id, complete)


# =========================================================
# HERO BANNER
# =========================================================
st.markdown(
    """
    <div class="live-hero">
        <div class="eyebrow">● CRICKET LIVE CENTRE</div>
        <div class="hero-art">🏏</div>
        <h1>Live <span>Matches</span></h1>
        <p>
            Follow live and recent cricket action, compare team scores,
            check match status and explore detailed batting and bowling
            scorecards in one place.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MATCHES AND SCORECARDS
# =========================================================
with friendly_errors("Live Matches"):
    top1, top2 = st.columns([3, 1], vertical_alignment="bottom")

    with top1:
        kind_label = st.radio(
            "Choose match category",
            ["Live", "Recent"],
            horizontal=True,
            key="live_matches_kind",
        )

    with top2:
        if st.button(
            "🔄 Refresh matches",
            use_container_width=True,
            type="primary",
        ):
            load_matches.clear()
            load_scorecard.clear()
            st.rerun()

    kind = kind_label.lower()

    try:
        with st.spinner("Fetching cricket matches..."):
            matches = load_matches(kind)
    except CricbuzzAPIError as exc:
        st.error(f"Could not reach the Cricbuzz API: {exc}")
        st.stop()

    if not matches:
        st.info(f"No {kind} matches are available right now.")
        st.stop()

    st.caption(
        f"🏏 {len(matches)} {kind} matches · "
        "Match list cached for 60 seconds"
    )

    # -----------------------------------------------------
    # MATCH CARDS
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-heading">🏟️ Match Centre</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-description">'
        'Select a match below to view its detailed scorecard.'
        '</div>',
        unsafe_allow_html=True,
    )

    visible_matches = matches[:20]

    for start in range(0, len(visible_matches), 2):
        row_matches = visible_matches[start:start + 2]
        columns = st.columns(2, gap="medium")

        for column, m in zip(columns, row_matches):
            with column:
                with st.container(border=True):
                    team1 = str(m.get("team1") or "Team 1")
                    team2 = str(m.get("team2") or "Team 2")
                    description = str(m.get("description") or "Match")
                    match_format = str(m.get("format") or "Cricket")
                    series = str(m.get("series") or "")
                    venue = str(m.get("venue") or "")
                    status = str(m.get("status") or m.get("state") or "")
                    score1 = str(m.get("score1") or "Score unavailable")
                    score2 = str(m.get("score2") or "Score unavailable")

                    st.markdown(
                        f"### {html.escape(team1)} vs "
                        f"{html.escape(team2)}"
                    )

                    st.markdown(
                        '<span class="match-label">'
                        f'{html.escape(match_format.upper())} · '
                        f'{html.escape(description)}</span>',
                        unsafe_allow_html=True,
                    )

                    if series:
                        st.caption(f"🏆 {series}")

                    # Score display
                    score_columns = st.columns(2, gap="small")

                    with score_columns[0]:
                        st.metric(
                            label=team1,
                            value=score1,
                        )

                    with score_columns[1]:
                        st.metric(
                            label=team2,
                            value=score2,
                        )

                    if status:
                        st.markdown(
                            '<div class="match-status">📌 '
                            f'{html.escape(status)}</div>',
                            unsafe_allow_html=True,
                        )

                    if venue:
                        st.caption(f"🏟️ {venue}")

                    match_id = m.get("match_id")

                    if match_id is None:
                        st.warning(
                            "This match has no match ID, so its scorecard "
                            "cannot be loaded."
                        )
                    else:
                        button_key = f"scorecard_{match_id}"

                        if st.button(
                            "📋 View this scorecard →",
                            key=button_key,
                            use_container_width=True,
                            type="primary",
                        ):
                            st.session_state["selected_scorecard_id"] = (
                                str(match_id)
                            )
                            st.session_state["selected_scorecard_label"] = (
                                f"{team1} vs {team2}"
                            )
                            st.session_state["scorecard_requested"] = True
                            st.rerun()

    # -----------------------------------------------------
    # DETAILED SCORECARD
    # -----------------------------------------------------
    if st.session_state.get("scorecard_requested", False):
        selected_id = st.session_state.get("selected_scorecard_id")
        selected_label = st.session_state.get(
            "selected_scorecard_label",
            "Selected match",
        )

        st.markdown(
            f"""
            <div class="scorecard-banner">
                <h3>📋 Detailed Scorecard</h3>
                <p>{html.escape(selected_label)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected_match = next(
            (
                match for match in matches
                if str(match.get("match_id")) == str(selected_id)
            ),
            None,
        )

        if selected_match is None:
            st.warning(
                "The selected match is not in the current match list. "
                "Refresh the list and select it again."
            )
        else:
            state = str(
                selected_match.get("state")
                or selected_match.get("status")
                or ""
            )
            complete = state.lower().startswith("complete")

            try:
                with st.spinner("Loading batting and bowling figures..."):
                    innings = load_scorecard(int(selected_id), complete)

            except CricbuzzAPIError as exc:
                st.error(f"Scorecard unavailable: {exc}")
                innings = None

            if innings is not None:
                if not innings:
                    st.info(
                        "No scorecard data is available for this match yet."
                    )
                else:
                    valid_innings = [
                        inning for inning in innings
                        if isinstance(inning, dict)
                    ]

                    if not valid_innings:
                        st.info(
                            "The API returned no displayable innings."
                        )
                    else:
                        tab_titles = [
                            str(
                                inning.get("title")
                                or f"Innings {index}"
                            )
                            for index, inning in enumerate(
                                valid_innings,
                                start=1,
                            )
                        ]

                        tabs = st.tabs(tab_titles)

                        for tab, inning in zip(tabs, valid_innings):
                            with tab:
                                total = inning.get("total")

                                if total:
                                    st.subheader(str(total))

                                batting = inning.get("batting") or []
                                bowling = inning.get("bowling") or []

                                st.markdown("#### 🏏 Batting")

                                if batting:
                                    st.dataframe(
                                        pd.DataFrame(batting),
                                        hide_index=True,
                                        use_container_width=True,
                                    )
                                else:
                                    st.info(
                                        "Batting figures are not available "
                                        "for this innings."
                                    )

                                extras = inning.get("extras")
                                if extras not in (None, ""):
                                    st.caption(f"Extras: {extras}")

                                st.markdown("#### 🎯 Bowling")

                                if bowling:
                                    st.dataframe(
                                        pd.DataFrame(bowling),
                                        hide_index=True,
                                        use_container_width=True,
                                    )
                                else:
                                    st.info(
                                        "Bowling figures are not available "
                                        "for this innings."
                                    )

        if st.button("✖ Close scorecard"):
            st.session_state["scorecard_requested"] = False
            st.rerun()


# =========================================================
# FOOTER
# =========================================================
st.divider()

footer_left, footer_right = st.columns(2)

with footer_left:
    st.caption("🏏 Cricbuzz LiveStats · Live cricket insights")

with footer_right:
    st.markdown(
        """
        <div style="text-align:right;color:#71829a;font-size:.8rem">
            Powered by Streamlit · SQLite · Cricbuzz API
        </div>
        """,
        unsafe_allow_html=True,
    )
