"""Top Player Stats page."""
import re

import streamlit as st

import config
from api.cricbuzz_client import CricbuzzAPIError
from services import chart_service
from services import player_service as ps
from utils.logger import get_logger
from utils.ui import friendly_errors
from utils.sidebar import render_sidebar

log = get_logger(__name__)

st.set_page_config(page_title="Top Player Stats", page_icon="📊", layout="wide")




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
        <div class="eyebrow">● TOP PLAYER STATS</div>
        <div class="hero-art">📊</div>
        <h1>Top Player <span>Stats</span></h1>
        <p>Explore player leaderboards, performance metrics and cricket statistics across match formats.</p>
    </div>
    """,
    unsafe_allow_html=True,
)



@st.cache_data(ttl=600, show_spinner=False)
def load_api(category: str, fmt: str):
    return ps.fetch_top_stats_api(category, fmt)


@st.cache_data(ttl=60, show_spinner=False)
def load_db(category: str, fmt: str):
    return ps.fetch_top_stats_db(category, fmt)


def is_id_column(name: str) -> bool:
    """True for columns like 'Player ID' or 'id' that are labels, not stats."""
    return re.search(r"\bid\b", str(name), re.I) is not None


def default_metric(category: str, metrics: list[str]) -> str:
    """Pick the column the category is about, e.g. 'Most Runs' -> 'Runs'."""
    cat = category.lower()
    for col in metrics:
        if col.lower() in cat:
            return col
    return metrics[0]


with friendly_errors("Top Stats"):
    c1, c2 = st.columns([2, 2])
    category = c1.selectbox("Category", list(ps.CATEGORIES))
    fmt = c2.radio("Format", list(ps.FORMAT_IDS), horizontal=True)

    df, source = None, ""
    if config.RAPIDAPI_KEY:
        try:
            with st.spinner("Loading leaderboard..."):
                df = load_api(category, fmt)
            source = "Live Cricbuzz API"
        except CricbuzzAPIError as exc:
            log.warning("Top stats API failed (%s, %s): %s", category, fmt, exc)
            st.warning(f"API unavailable ({exc}). "
                       "Showing database data instead.")
    if df is None or df.empty:
        df = load_db(category, fmt)
        source = "Local database (may be sample data)"

    if df.empty:
        st.info("No data for this selection yet.")
        st.stop()

    st.caption(f"Source: {source}")
    st.dataframe(df, hide_index=True, use_container_width=True)

    # ---- Chart: ranked bar of the metric this category is about --------
    text_cols = [c for c in df.columns if df[c].dtype == object]
    metrics = [c for c in df.columns
               if str(df[c].dtype).startswith(("int", "float"))
               and not is_id_column(c)]

    if text_cols and metrics:
        label = text_cols[0]
        metric = st.selectbox(
            "Chart value", metrics,
            index=metrics.index(default_metric(category, metrics)))
        top = df.nlargest(10, metric)
        st.plotly_chart(
            chart_service.ranking_bar(
                top, label, metric, f"Top 10 by {metric} ({fmt})"),
            use_container_width=True)