"""CRUD Operations page: manage player records."""
from dataclasses import asdict

import pandas as pd
import streamlit as st

from models.player import Player
from services import crud_service as svc
from utils.exceptions import AppError
from utils.ui import friendly_errors
from utils.validators import ROLES
from utils.sidebar import render_sidebar

st.set_page_config(page_title="CRUD Operations", page_icon="🛠", layout="wide")


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
        <div class="eyebrow">● PLAYER DATA MANAGEMENT</div>
        <div class="hero-art">🛠️</div>
        <h1>Player <span>Management</span></h1>
        <p>Add, review, update and manage player records in your local cricket database.</p>
    </div>
    """,
    unsafe_allow_html=True,
)



ROLE_OPTIONS = [""] + sorted(ROLES)


def blank_to_none(value: str):
    value = (value or "").strip()
    return value or None


def player_form(prefix: str, team_labels: dict, p: Player | None = None) -> dict:
    """Render the shared field widgets; return the entered values."""
    p = p or Player(full_name="", country="")
    team_names = list(team_labels)
    current_team = next((n for n, i in team_labels.items()
                         if i == p.team_id), "(none)")
    c1, c2 = st.columns(2)
    name = c1.text_input("Full name *", p.full_name, key=f"{prefix}_name")
    country = c2.text_input("Country *", p.country, key=f"{prefix}_country")
    role = c1.selectbox(
        "Playing role", ROLE_OPTIONS,
        index=ROLE_OPTIONS.index(p.playing_role or ""), key=f"{prefix}_role")
    team = c2.selectbox("Team", team_names,
                        index=team_names.index(current_team),
                        key=f"{prefix}_team")
    bat = c1.text_input("Batting style", p.batting_style or "",
                        key=f"{prefix}_bat")
    bowl = c2.text_input("Bowling style", p.bowling_style or "",
                         key=f"{prefix}_bowl")
    dob = c1.text_input("Date of birth (YYYY-MM-DD)", p.date_of_birth or "",
                        key=f"{prefix}_dob")
    return {
        "full_name": name, "country": country,
        "playing_role": blank_to_none(role),
        "batting_style": blank_to_none(bat),
        "bowling_style": blank_to_none(bowl),
        "date_of_birth": blank_to_none(dob),
        "team_id": team_labels[team],
    }


with friendly_errors("CRUD"):
    teams = svc.list_teams()
    TEAM_LABELS = {"(none)": None, **{name: tid for tid, name in teams}}

    tab_view, tab_add, tab_edit, tab_del = st.tabs(
        ["📋 View", "➕ Add", "✏️ Edit", "🗑 Delete"])

    # ---- View -------------------------------------------------------------
    with tab_view:
        c1, c2, c3 = st.columns([3, 2, 1])
        search = c1.text_input("Search by name")
        country_filter = c2.text_input("Country (exact)")
        page = c3.number_input("Page", min_value=1, value=1, step=1)
        players = svc.list_players(search.strip(), country_filter.strip(),
                                   page=int(page), page_size=25)
        if players:
            st.dataframe(pd.DataFrame([asdict(p) for p in players]),
                         hide_index=True, use_container_width=True)
        else:
            st.info("No players match.")

    # ---- Add --------------------------------------------------------------
    with tab_add:
        with st.form("add_form", clear_on_submit=True):
            values = player_form("add", TEAM_LABELS)
            submitted = st.form_submit_button("Add player", type="primary")
        if submitted:
            try:
                new_id = svc.create_player(Player(**values))
                st.success(f"Player added (ID {new_id}).")
            except AppError as exc:
                st.error(str(exc))

    # ---- Edit -------------------------------------------------------------
    with tab_edit:
        all_players = svc.list_players(page_size=500)
        if not all_players:
            st.info("No players to edit.")
        else:
            pick = st.selectbox(
                "Choose a player", all_players,
                format_func=lambda p: f"{p.full_name} ({p.country}) · ID {p.player_id}",
                key="edit_pick")
            with st.form(f"edit_form_{pick.player_id}"):
                values = player_form(f"edit{pick.player_id}", TEAM_LABELS, pick)
                saved = st.form_submit_button("Save changes", type="primary")
            if saved:
                try:
                    svc.update_player(pick.player_id, values)
                    st.success("Changes saved. Switch tabs or refresh to see them.")
                except AppError as exc:
                    st.error(str(exc))

    # ---- Delete -----------------------------------------------------------
    with tab_del:
        candidates = svc.list_players(page_size=500)
        if not candidates:
            st.info("No players to delete.")
        else:
            victim = st.selectbox(
                "Choose a player to delete", candidates,
                format_func=lambda p: f"{p.full_name} ({p.country}) · ID {p.player_id}",
                key="del_pick")
            st.warning(f"This permanently deletes **{victim.full_name}**.")
            confirm = st.checkbox("I understand this cannot be undone",
                                  key=f"confirm_{victim.player_id}")
            if st.button("Delete player", disabled=not confirm):
                try:
                    svc.delete_player(victim.player_id)
                    st.success("Player deleted.")
                    st.rerun()
                except AppError as exc:
                    st.error(str(exc))