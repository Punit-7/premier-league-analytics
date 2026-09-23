"""Streamlit front end. Reads the database, computes nothing.

TODO: implement the actual report pages. See the build guide, stage 14.
"""
import duckdb
import pandas as pd
import streamlit as st

from src.config import CONFIG
from src.logging_setup import get_logger

log = get_logger(__name__)

DB = CONFIG["paths"]["database"]

st.title("Premier League Analytics")


@st.cache_data(ttl=3600)
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    with duckdb.connect(str(DB), read_only=True) as conn:
        return conn.execute(sql, params).df()


with st.sidebar.expander("Pipeline health"):
    try:
        refresh = query("SELECT * FROM refresh_log")
    except duckdb.CatalogException:
        refresh = pd.DataFrame()
    if refresh.empty:
        st.caption("No run records yet.")
    else:
        last = refresh.iloc[-1]
        st.success(f"Last refresh: {last['refreshed_at']}")
        st.dataframe(refresh.tail(10), hide_index=True, use_container_width=True)
