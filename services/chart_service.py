"""Chart builders. DataFrame in, Plotly figure out. No Streamlit here."""
import pandas as pd
import plotly.express as px

CHART_TYPES = ["Bar", "Line", "Pie", "Scatter"]
MAX_CATEGORIES = 25          # keep bars and slices readable


def build_chart(kind: str, df: pd.DataFrame, x: str, y: str, title: str):
    """Return a Plotly figure for the chosen chart type."""
    if kind == "Bar":
        fig = px.bar(df.head(MAX_CATEGORIES), x=x, y=y, title=title)
    elif kind == "Line":
        fig = px.line(df, x=x, y=y, markers=True, title=title)
    elif kind == "Pie":
        fig = px.pie(df.head(MAX_CATEGORIES), names=x, values=y,
                     hole=0.4, title=title)
    elif kind == "Scatter":
        fig = px.scatter(df, x=x, y=y, title=title)
    else:
        raise ValueError(f"Unknown chart type: {kind}")
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    return fig


def ranking_bar(df: pd.DataFrame, label: str, value: str, title: str):
    """Horizontal ranking bar with the largest value at the top."""
    data = df.sort_values(value, ascending=True)
    fig = px.bar(data, x=value, y=label, orientation="h",
                 text=value, title=title)
    fig.update_layout(yaxis_title=None, margin=dict(l=0, r=0, t=50, b=0))
    return fig


def form_line(df: pd.DataFrame, x: str, y: str, title: str, hover: str):
    """Runs per innings in date order, with the match as hover text."""
    fig = px.line(df, x=x, y=y, markers=True, title=title,
                  hover_data=[hover])
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    return fig


def avg_vs_strike_scatter(df: pd.DataFrame, title: str):
    """One dot per batter: average (x) vs strike rate (y), sized by runs."""
    fig = px.scatter(df, x="average", y="strike_rate", size="runs",
                     hover_name="player", title=title)
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    return fig