
"""Shared branded sidebar for all Cricbuzz LiveStats pages."""

import streamlit as st


def render_sidebar():
    """Render the same branded navigation on every page."""

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(
                180deg, #061735 0%, #0b2b54 65%, #041329 100%
            );
        }

        /* Hide Streamlit's automatic navigation containing 'app'. */
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        section[data-testid="stSidebar"] nav[aria-label="pages"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] {
            margin: 5px 0 !important;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: 100% !important;
            min-height: 44px !important;
            padding: 10px 12px !important;
            border: 1px solid transparent !important;
            border-radius: 11px !important;
            background: transparent !important;
            color: #e6f0ff !important;
            text-decoration: none !important;
            font-weight: 500 !important;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a * {
            color: #e6f0ff !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: rgba(73, 151, 255, .18) !important;
            border-color: rgba(120, 183, 255, .35) !important;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] .stCaption {
            color: #dce9ff !important;
        }

        .cricbuzz-brand {
            padding: 8px 5px 22px;
            border-bottom: 1px solid rgba(180, 210, 255, .14);
            margin-bottom: 22px;
        }

        .cricbuzz-logo {
            font-size: 2.3rem;
            margin-bottom: 8px;
        }

        .cricbuzz-brand-title {
            color: #ffffff;
            font-size: 1.65rem;
            font-weight: 850;
            line-height: 1.1;
        }

        .cricbuzz-brand-title span {
            color: #38c7ff;
        }

        .cricbuzz-brand-caption {
            color: #a9c2e2;
            font-size: .72rem;
            margin-top: 12px;
            letter-spacing: .06em;
        }

        .cricbuzz-nav-heading {
            color: #829bb9;
            font-size: .78rem;
            font-weight: 750;
            letter-spacing: .05em;
            margin: 0 0 12px 0;
        }

        .cricbuzz-sidebar-footer {
            border-top: 1px solid rgba(180, 210, 255, .14);
            margin-top: 24px;
            padding: 18px 5px 8px;
            color: #a9c2e2;
            font-size: .76rem;
            line-height: 1.8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            """
            <div class="cricbuzz-brand">
                <div class="cricbuzz-logo">🏏</div>
                <div class="cricbuzz-brand-title">
                    Cricbuzz<br><span>LiveStats</span>
                </div>
                <div class="cricbuzz-brand-caption">
                    CRICKET · DATA · INSIGHTS
                </div>
            </div>
            <div class="cricbuzz-nav-heading">NAVIGATION</div>
            """,
            unsafe_allow_html=True,
        )

        st.page_link("app.py", label="Dashboard", icon="🏠")
        st.page_link(
            "pages/1_Live_Matches.py",
            label="Live Matches",
            icon="📡",
        )
        st.page_link(
            "pages/2_Top_Stats.py",
            label="Top Player Stats",
            icon="📊",
        )
        st.page_link(
            "pages/3_SQL_Queries.py",
            label="SQL Analytics",
            icon="🔎",
        )
        st.page_link(
            "pages/4_CRUD_Operations.py",
            label="Player Management",
            icon="🛠️",
        )
        st.page_link(
            "pages/6_Charts.py",
            label="Charts & Trends",
            icon="📈",
        )
        st.page_link(
            "pages/5_Settings.py",
            label="Settings",
            icon="⚙️",
        )

        st.markdown(
            """
            <div class="cricbuzz-sidebar-footer">
                🏏 REAL-TIME CRICKET ANALYTICS<br>
                Built with Streamlit + SQLite
            </div>
            """,
            unsafe_allow_html=True,
        )
