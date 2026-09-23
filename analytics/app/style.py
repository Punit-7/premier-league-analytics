"""Design tokens and injected CSS. One place, so the app stays coherent."""
import streamlit as st

INK = "#16191A"
MUTED = "#5E6763"
LINE = "#D6DAD2"
SURFACE = "#FFFFFF"
ACCENT = "#1F6A4A"

# Fixed per position, so a colour means the same thing on every chart.
POSITION_COLORS = {
    "GKP": "#8C6D3F",
    "DEF": "#2F6F8F",
    "MID": "#1F6A4A",
    "FWD": "#A6452E",
}

PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color=INK),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=8, r=8, t=28, b=8),
    xaxis=dict(gridcolor=LINE, zeroline=False),
    yaxis=dict(gridcolor=LINE, zeroline=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=""),
)

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:wght@500&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

.block-container {{ padding-top: 2.2rem; max-width: 1320px; }}

h1, h2, h3 {{
    font-family: 'Newsreader', Georgia, serif !important;
    font-weight: 500 !important;
    letter-spacing: -.01em;
}}

div[data-testid="stMetric"] {{
    background: {SURFACE};
    border: 1px solid {LINE};
    border-radius: 4px;
    padding: 14px 16px;
}}
div[data-testid="stMetricLabel"] {{ color: {MUTED}; font-size: .8rem; }}
div[data-testid="stMetricValue"] {{ font-size: 1.7rem; font-weight: 600; }}

section[data-testid="stSidebar"] {{ border-right: 1px solid {LINE}; }}
div[data-testid="stDataFrame"] {{ border: 1px solid {LINE}; border-radius: 4px; }}
header[data-testid="stHeader"] {{ background: transparent; }}

.freshness {{
    color: {MUTED};
    font-size: .82rem;
    border-left: 3px solid {ACCENT};
    padding: 2px 0 2px 10px;
    margin-bottom: 18px;
}}
</style>
"""


def apply_style() -> None:
    st.markdown(CSS, unsafe_allow_html=True)