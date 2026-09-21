"""Streamlit front end. Reads the database, computes nothing.

TODO: implement. See the build guide for this stage.
"""
from src.logging_setup import get_logger

log=get_logger(__name__)

health = query("""
               SELECT stage, status, duration_s, finished_at
               FROM pipeline_run
               WHERE run_id = (SELECT run_id FROM pipeline_run 
               ORDER BY finished_at DESC LIMIT 1)
               ORDER BY finished_at               
""")

with st.sidebar.expander("Pipeline health"):
    if health.empty:
        st.caption("No run records yet.")
    else:
        failed = health[health["status"] != "ok"]
        if failed.empty:
            st.success(f"Last run: all {len(health)} stages ok "
                       f"in {health['duration_s'].sum():.0f}s")
        else:
            st.error(f"Last run: {len(failed)} stage(s) failed")
        st.dataframe(health, hide_index=True, use_container_width=True)