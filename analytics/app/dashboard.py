from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from app.style import POSITION_COLORS, PLOTLY_LAYOUT, apply_style

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "processed" / "epl.duckdb"
SQL = ROOT / "sql" / "analysis"

st.set_page_config(page_title="Premier League Analytics · FPL Tracker",
                   page_icon="⚽", layout="wide")
apply_style()


@st.cache_data(ttl=3600)
def q(sql: str, params: tuple = ()) -> pd.DataFrame:
    # Read-only: the running app must not hold a write lock that the
    # 6am refresh job needs.
    with duckdb.connect(str(DB), read_only=True) as conn:
        return conn.execute(sql, params).df()


def sql_file(name: str) -> str:
    """Load a committed query by name, whatever directory Streamlit runs from."""
    return (SQL / name).read_text(encoding="utf-8")


def styled(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


if not DB.exists():
    st.error("Database not found. Run `make all` — see the README.")
    st.stop()

fresh = q("SELECT * FROM refresh_log ORDER BY refreshed_at DESC LIMIT 1")
st.title("Premier League · Live Season & FPL Tracker")
st.markdown(
    f"<div class='freshness'>Gameweek {fresh.loc[0,'latest_gameweek']} · "
    f"{int(fresh.loc[0,'live_matches'])} matches played · "
    f"refreshed {fresh.loc[0,'refreshed_at']} UTC</div>",
    unsafe_allow_html=True,
)

players = q("SELECT * FROM player_season")
if players.empty:
    st.warning("No player data yet this season.")
    st.stop()

st.sidebar.header("Filters")
positions = st.sidebar.multiselect(
    "Position", sorted(players["position_short"].unique()),
    default=sorted(players["position_short"].unique()))
max_price = st.sidebar.slider("Max price (£m)", 3.5,
                              float(players["price_m"].max()),
                              float(players["price_m"].max()), 0.5)
min_minutes = st.sidebar.slider("Minimum minutes", 0, 900, 270, 90)

view = players[players["position_short"].isin(positions)
               & (players["price_m"] <= max_price)
               & (players["minutes"] >= min_minutes)]
if view.empty:
    st.warning("No players match those filters. Widen the price or minutes range.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Players shown", len(view))
c2.metric("Best value", f"{view['points_per_million'].max():.1f} pts/£m"
          if not view.empty else "—")
c3.metric("Median price", f"£{view['price_m'].median():.1f}m"
          if not view.empty else "—")

st.subheader("Value: points against price")
fig = px.scatter(view, x="price_m", y="points", color="position_short",
                 color_discrete_map=POSITION_COLORS,
                 size="selected_by_percent", hover_name="web_name",
                 hover_data=["team_name", "points_per_million", "minutes"],
                 labels={"price_m": "Price (£m)", "points": "Season points",
                         "position_short": ""})
fig.update_traces(marker=dict(line=dict(width=0.5, color="white"), opacity=0.85))
fig.update_layout(height=460)
st.plotly_chart(styled(fig), use_container_width=True)
st.caption("Bubble size is ownership. Players sitting above the cloud at a "
           "given price are the ones beating what they cost.")

left, right = st.columns(2)
with left:
    st.subheader("Best value per million")
    st.dataframe(
        view.nlargest(15, "points_per_million")[
            ["web_name", "team_name", "position_short", "price_m",
             "points", "points_per_million"]],
        use_container_width=True, hide_index=True)

with right:
    st.subheader("Easiest fixtures, next 5 gameweeks")
    st.dataframe(q(sql_file("04_fixture_difficulty.sql")),
                 use_container_width=True, hide_index=True)

st.subheader("Player detail")
pick = st.selectbox("Player", view.sort_values("points", ascending=False)["web_name"])
detail = q("""
    SELECT f.gameweek_id, f.total_points, f.minutes, f.bonus, f.price_m,
           o.team_name AS opponent, f.was_home
    FROM fact_player_fixture f
    JOIN dim_player p ON p.player_id = f.player_id
    LEFT JOIN dim_team o ON o.team_id = f.opponent_team_id
    WHERE p.web_name = ?
    ORDER BY f.gameweek_id
""", (pick,))
fig2 = px.bar(detail, x="gameweek_id", y="total_points",
              hover_data=["opponent", "minutes", "bonus"],
              labels={"gameweek_id": "Gameweek", "total_points": "Points"})
fig2.update_traces(marker_color="#1F6A4A")
fig2.update_layout(height=300)
st.plotly_chart(styled(fig2), use_container_width=True)
st.caption("One tall bar is a single good week, not form.")