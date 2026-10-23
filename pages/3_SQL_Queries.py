"""SQL Queries and Analytics page."""
import sqlite3

import streamlit as st

from services import analytics_service as svc
from services import chart_service
from utils.exceptions import AppError
from utils.ui import friendly_errors
from utils.sidebar import render_sidebar

st.set_page_config(page_title="SQL Analytics", page_icon="🔍", layout="wide")


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
        <div class="eyebrow">● CRICKET ANALYTICS LAB</div>
        <div class="hero-art">🔎</div>
        <h1>SQL <span>Analytics</span></h1>
        <p>Explore curated cricket questions, run read-only SQL and turn results into useful charts.</p>
    </div>
    """,
    unsafe_allow_html=True,
)



def show_result(df, secs, prefix, csv_name):
    """Table, CSV download and an optional chart for one query result."""
    if df.empty:
        st.info("The query ran but returned no rows. "
                "That usually means the data it needs isn't loaded yet.")
        return

    st.caption(f"{len(df):,} rows · {secs * 1000:.0f} ms")
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.download_button("Download CSV", df.to_csv(index=False),
                       file_name=csv_name, mime="text/csv",
                       key=f"{prefix}_csv")

    # ---- Chart -------------------------------------------------------
    numeric = list(df.select_dtypes("number").columns)
    if len(df) < 2 or not numeric:
        return                      # nothing sensible to plot

    all_cols = list(df.columns)
    labels = [c for c in all_cols if c not in numeric] or all_cols

    with st.expander("📊 Chart this result", expanded=True):
        c1, c2, c3 = st.columns(3)
        kind = c1.selectbox("Chart type", chart_service.CHART_TYPES,
                            key=f"{prefix}_kind")
        x = c2.selectbox("X axis / labels", all_cols,
                         index=all_cols.index(labels[0]),
                         key=f"{prefix}_x")
        y = c3.selectbox("Y axis / values", numeric, key=f"{prefix}_y")
        try:
            fig = chart_service.build_chart(kind, df, x, y, f"{y} by {x}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:        # a bad column combo must not crash
            st.warning(f"Could not draw this chart: {exc}")


with friendly_errors("SQL Analytics"):
    tab_q, tab_c = st.tabs(["Analytics questions", "Custom SQL"])

    # ---- Tab 1: saved questions -------------------------------------------
    with tab_q:
        levels = ["All"] + sorted({q.level for q in svc.QUERIES},
                                  key=["Beginner", "Intermediate",
                                       "Advanced"].index)
        level = st.radio("Level", levels, horizontal=True)
        options = [q for q in svc.QUERIES if level in ("All", q.level)]
        chosen = st.selectbox("Question", options,
                              format_func=lambda q: q.title)

        try:
            sql_text = svc.load_sql(chosen.key)
        except AppError as exc:
            st.error(str(exc))
            st.stop()

        with st.expander("Show SQL"):
            st.code(sql_text, language="sql")

        if st.button("Run query", type="primary"):
            try:
                with st.spinner("Running..."):
                    df, secs = svc.run_named_query(chosen.key)
            except (sqlite3.Error, AppError) as exc:
                st.session_state.pop("named_result", None)
                st.error(f"Query failed: {exc}")
            else:
                st.session_state["named_result"] = {
                    "key": chosen.key, "df": df, "secs": secs}

        # Show the stored result only if it belongs to the selected question.
        stored = st.session_state.get("named_result")
        if stored and stored["key"] == chosen.key:
            show_result(stored["df"], stored["secs"],
                        prefix=f"named_{chosen.key}",
                        csv_name=f"{chosen.key}.csv")

    # ---- Tab 2: custom SQL ------------------------------------------------
    with tab_c:
        st.caption("Read-only. One SELECT (or WITH) statement. "
                   f"Results are limited to {svc.MAX_ROWS:,} rows.")
        user_sql = st.text_area("Your query", height=180,
                                value="SELECT * FROM players LIMIT 10;")
        if st.button("Run custom query"):
            try:
                df, secs = svc.run_custom_sql(user_sql)
            except AppError as exc:
                st.session_state.pop("custom_result", None)
                st.error(str(exc))
            except sqlite3.Error as exc:
                st.session_state.pop("custom_result", None)
                st.error(f"Database error: {exc}")
            else:
                st.session_state["custom_result"] = {"df": df, "secs": secs}

        stored = st.session_state.get("custom_result")
        if stored:
            show_result(stored["df"], stored["secs"],
                        prefix="custom", csv_name="custom_query.csv")