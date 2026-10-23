"""Settings page: API status, data refresh, cache, database info."""
import sqlite3

import pandas as pd
import streamlit as st

import config
from api.cricbuzz_client import CricbuzzAPIError
from services import settings_service as svc
from utils.ui import friendly_errors
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")


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
        <div class="eyebrow">● SYSTEM CONTROL CENTRE</div>
        <div class="hero-art">⚙️</div>
        <h1>App <span>Settings</span></h1>
        <p>Check API configuration, refresh available data and inspect your local SQLite database.</p>
    </div>
    """,
    unsafe_allow_html=True,
)



with friendly_errors("Settings"):
    # ---- API --------------------------------------------------------------
    st.markdown("### Cricbuzz API")
    if svc.api_key_configured():
        st.success("API key is configured.")
    else:
        st.warning("No API key found. Add RAPIDAPI_KEY to your `.env` file "
                   "and restart the app.")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Test API connection",
                     disabled=not svc.api_key_configured()):
            try:
                with st.spinner("Calling the API..."):
                    n = svc.test_api()
                st.success(f"Connected. The API returned {n} recent matches.")
            except CricbuzzAPIError as exc:
                st.error(f"API check failed: {exc}")

    with c2:
        if st.button("Refresh recent matches into database",
                     disabled=not svc.api_key_configured()):
            try:
                with st.spinner("Fetching and saving..."):
                    saved = svc.refresh_recent_matches()
                st.cache_data.clear()
                st.success(f"Processed {saved} matches. "
                           "Duplicates are ignored automatically.")
            except CricbuzzAPIError as exc:
                st.error(f"Refresh failed: {exc}")
            except sqlite3.Error as exc:
                st.error(f"Database error while saving: {exc}")

    with st.expander("Configuration (no secrets shown)"):
        st.write({
            "API host": config.RAPIDAPI_HOST,
            "Request timeout (s)": config.REQUEST_TIMEOUT,
            "Max retries": config.MAX_RETRIES,
        })

    # ---- Cache ------------------------------------------------------------
    st.markdown("### Cache")
    st.caption("Live Matches and Top Stats cache API results to protect "
               "your quota.")
    if st.button("Clear cached data"):
        st.cache_data.clear()
        st.success("Cache cleared. The next page load fetches fresh data.")

    # ---- Database ---------------------------------------------------------
    st.markdown("### Database")
    try:
        info = svc.database_info()
    except sqlite3.Error as exc:
        st.error(f"Cannot read the database: {exc}. "
                 "Run `python scripts/init_db.py`.")
    else:
        m1, m2 = st.columns(2)
        m1.metric("File size", f"{info['size_kb']:,} KB")
        m2.metric("Total rows", f"{sum(info['counts'].values()):,}")
        st.caption(f"Location: `{info['path']}`")
        st.dataframe(
            pd.DataFrame({"Table": list(info["counts"]),
                          "Rows": list(info["counts"].values())}),
            hide_index=True, use_container_width=True)