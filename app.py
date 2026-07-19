import streamlit as st

from Database.db_setup import create_tables, seed_data
from Frontend.UI_components import (
    init_session_state,
    render_dashboard_metrics,
    render_dashboard_panels,
    render_page_shell,
    render_queue_monitor,
    render_sidebar_inputs,
    serve_next_call_callback,
)
from Frontend.charts import render_analytics_dashboard


st.set_page_config(
    page_title="Call Center Waiting Line System",
    page_icon=":telephone_receiver:",
    layout="wide",
    initial_sidebar_state="expanded",
)

create_tables()
seed_data()
init_session_state()

render_page_shell()
render_sidebar_inputs()

tab_dashboard, tab_analytics = st.tabs(["Operations", "Analytics"])

with tab_dashboard:
    render_dashboard_panels()
    st.button(
        "Serve Next Call",
        on_click=serve_next_call_callback,
        type="primary",
        use_container_width=True,
    )
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    render_dashboard_metrics()
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    render_queue_monitor()

with tab_analytics:
    render_analytics_dashboard()
