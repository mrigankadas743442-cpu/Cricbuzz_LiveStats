"""Charts page: four visualizations on real harvested data."""
import streamlit as st

from services import chart_data_service as data
from services import chart_service as charts
from utils.ui import friendly_errors
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Charts", page_icon="📊", layout="wide")


# Shared blue dashboard theme. Keep page logic below this block unchanged.
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
        background: linear-gradient(135deg,#f5f9ff 0%,#edf4fc 55%,#f8fbff 100%);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: rgba(245,249,255,.94); }
    .block-container { max-width: 1500px; padding: 1.5rem 1.6rem 2.5rem; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,#061735 0%,#0b2b54 58%,#041329 100%) !important;
        border-right: 1px solid rgba(75,160,255,.18);
    }
    [data-testid="stSidebar"] > div:first-child { background: transparent !important; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] a { color: #e5efff; }
    /* Hide Streamlit's automatically generated app.py link, not our custom Dashboard link. */
    [data-testid="stSidebarNav"] > div > ul > li:first-child { display: none !important; }
    [data-testid="stSidebarNav"] a {
        color: #dce9ff !important; background: transparent !important;
        border: 1px solid transparent !important; border-radius: 10px !important;
        margin: 3px 8px !important; padding: 10px 12px !important;
        transition: all .18s ease;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(35,119,235,.22) !important;
        border-color: rgba(79,166,255,.35) !important; color: #fff !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(100deg,#0878f9,#075acb) !important;
        color: #fff !important; border-color: #258cff !important;
        font-weight: 750 !important; box-shadow: 0 5px 15px rgba(0,89,220,.22);
    }
    [data-testid="stSidebar"] hr { border-color: rgba(195,219,255,.15) !important; }
    .sidebar-brand {
        padding: 12px 5px 20px; margin: 0 8px 18px;
        border-bottom: 1px solid rgba(195,219,255,.15);
    }
    .sidebar-brand .brand-icon { font-size: 2.25rem; line-height: 1.2; margin-bottom: 8px; }
    .sidebar-brand .brand-name { color:#fff; font-size:1.6rem; font-weight:850; line-height:1.12; }
    .sidebar-brand .brand-name span { color:#38c7ff !important; }
    .sidebar-brand .brand-caption { color:#9bb6d9 !important; font-size:.7rem; letter-spacing:.08em; margin-top:10px; }
    .page-hero {
        position:relative; overflow:hidden; padding:27px 30px; margin:0 0 23px;
        border-radius:22px; color:#fff;
        background: radial-gradient(circle at 91% 12%,rgba(56,199,255,.34),transparent 31%),
                    linear-gradient(115deg,#061735,#0d3b75 62%,#0878a9);
        box-shadow:0 12px 32px rgba(10,48,100,.16);
    }
    .page-hero .eyebrow {
        display:inline-block; color:#a6edff; background:rgba(56,199,255,.13);
        border:1px solid rgba(106,220,255,.32); border-radius:25px;
        padding:6px 12px; font-size:.74rem; font-weight:800; letter-spacing:.07em;
    }
    .page-hero h1 { color:#fff !important; font-size:clamp(2rem,4vw,3rem) !important; line-height:1.15; margin:16px 0 8px; }
    .page-hero h1 span { color:#38c7ff; }
    .page-hero p { color:#d8eaff; line-height:1.65; margin:0; max-width:850px; }
    .page-hero .hero-art { position:absolute; right:28px; top:22px; font-size:4.7rem; opacity:.24; transform:rotate(-12deg); pointer-events:none; }
    [data-testid="stMetric"] {
        background:linear-gradient(145deg,#fff,#f4f8ff); border:1px solid #dce8f7;
        border-radius:13px; padding:12px 14px; box-shadow:0 4px 14px rgba(17,59,110,.045);
    }
    [data-testid="stMetricLabel"] { color:#627895; font-weight:700; }
    [data-testid="stMetricValue"] { color:#0a2d60; font-weight:850; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background:rgba(255,255,255,.94); border:1px solid #d8e6f7 !important;
        border-radius:16px !important; padding:12px 15px !important;
        box-shadow:0 5px 20px rgba(25,66,117,.045);
    }
    .stButton > button, [data-testid="stDownloadButton"] button {
        border-radius:10px; font-weight:700; min-height:42px; transition:all .15s ease;
    }
    .stButton > button[kind="primary"] {
        background:linear-gradient(100deg,#0878f9,#075dd7); border:1px solid #0878f9; color:white;
    }
    .stButton > button[kind="primary"]:hover { background:#075acb; border-color:#075acb; color:#fff; }
    [data-testid="stDataFrame"] { border:1px solid #dce8f7; border-radius:10px; overflow:hidden; }
    div[data-baseweb="tab-list"] { gap:8px; }
    button[data-baseweb="tab"] { border-radius:8px 8px 0 0; }
    hr { border-color:#dce8f7; }
    @media(max-width:700px) {
        .block-container { padding:1rem .7rem 2rem; }
        .page-hero { padding:22px 18px; }
        .page-hero .hero-art { right:12px; font-size:3rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_sidebar()


st.markdown(
    """
    <div class="page-hero">
        <div class="eyebrow">● CRICKET DATA STORIES</div>
        <div class="hero-art">📈</div>
        <h1>Charts <span>& Trends</span></h1>
        <p>Visualise run scorers, player form, team wins and batting performance from your stored data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)



st.caption("Built from the scorecards you have harvested. "
           "More harvested matches means richer charts.")


@st.cache_data(ttl=300, show_spinner=False)
def cached(name: str, *args):
    return getattr(data, name)(*args)


def empty_note():
    st.info("Not enough data yet. Harvest more matches, then run "
            "`python scripts/build_from_cache.py`.")


with friendly_errors("Charts"):
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Top scorers", "Player form", "Team wins", "Average vs strike rate"])

    # ---- 1. Top scorers (bar) -------------------------------------------
    with tab1:
        c1, c2 = st.columns(2)
        fmt = c1.selectbox("Format", ["All", "Test", "ODI", "T20I"])
        limit = c2.slider("How many players", 5, 20, 10)
        df = cached("top_scorers", fmt, limit)
        if df.empty:
            empty_note()
        else:
            st.plotly_chart(
                charts.ranking_bar(df, "player", "runs",
                                   f"Top {len(df)} run scorers ({fmt})"),
                use_container_width=True)

    # ---- 2. Player form (line) ------------------------------------------
    with tab2:
        players = cached("batters")
        if players.empty:
            empty_note()
        else:
            name = st.selectbox("Player", players["player"])
            pid = int(players.loc[players["player"] == name,
                                  "player_id"].iloc[0])
            df = cached("player_form", pid)
            st.plotly_chart(
                charts.form_line(df, "date", "runs",
                                 f"{name}: runs per innings", "match"),
                use_container_width=True)
            st.caption(f"{len(df)} innings recorded")

    # ---- 3. Team wins (pie) ---------------------------------------------
    with tab3:
        df = cached("wins_by_team")
        if df.empty:
            empty_note()
        else:
            st.plotly_chart(
                charts.build_chart("Pie", df, "team", "wins",
                                   "Wins by team"),
                use_container_width=True)

    # ---- 4. Average vs strike rate (scatter) ----------------------------
    with tab4:
        min_balls = st.slider("Minimum balls faced", 10, 300, 30, step=10)
        df = cached("average_vs_strike_rate", min_balls)
        if len(df) < 2:
            empty_note()
        else:
            st.plotly_chart(
                charts.avg_vs_strike_scatter(
                    df, "Batting average vs strike rate"),
                use_container_width=True)