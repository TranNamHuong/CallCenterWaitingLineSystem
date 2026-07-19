import streamlit as st

from Backend.queue_manager import CallCenterQueueManager


SERVICE_OPTIONS = [
    "Technical Support",
    "Billing",
    "Product Consultation",
    "Service Complaint",
    "Password Reset",
    "Insurance Request",
    "New Order",
    "Account Check",
    "Service Cancellation",
    "Other",
]

VIP_LABELS = {
    30: "Platinum VIP",
    20: "Gold VIP",
    10: "Silver VIP",
}


def init_session_state():
    """Initialize shared queue manager for the Streamlit session."""
    if "queue_manager" not in st.session_state:
        st.session_state.queue_manager = CallCenterQueueManager(max_size=50)
    if "current_serving" not in st.session_state:
        st.session_state.current_serving = None


def render_page_shell():
    """Render the global page styling and top-level header."""
    queue_manager = st.session_state.queue_manager
    total_waiting = queue_manager.get_total_waiting()
    vip_waiting = queue_manager.get_vip_queue_size()
    normal_waiting = queue_manager.normal_queue.size()
    current = st.session_state.current_serving

    status_html = (
        f"""
        <div class="hero-status live">
            <div class="hero-status-label">Now Serving</div>
            <div class="hero-status-value">{current['name']}</div>
            <div class="hero-status-meta">{current['type']} | {current['detail']} | {current['time']}</div>
        </div>
        """
        if current
        else """
        <div class="hero-status idle">
            <div class="hero-status-label">Operator Status</div>
            <div class="hero-status-value">Ready for next caller</div>
            <div class="hero-status-meta">No active call in progress</div>
        </div>
        """
    )

    st.markdown(
        """
        <style>
        :root {
            --bg: #f6f7f9;
            --panel: rgba(255, 255, 255, 0.96);
            --panel-strong: #ffffff;
            --line: rgba(15, 23, 42, 0.10);
            --text: #172033;
            --muted: #667085;
            --heading: #14213d;
            --tab-text: #334155;
            --input-bg: #ffffff;
            --input-border: #9fbfc1;
            --input-text: #1f2320;
            --input-placeholder: #98a2b3;
            --brand: #1f5c4d;
            --brand-2: #3f8f7f;
            --brand-3: #dcebe5;
            --warn: #c58a2c;
            --vip: #1f5c4d;
            --normal: #3e6c8f;
            --shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
        }
        html, body, [class*="css"]  {
            font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        }
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(31, 92, 77, 0.08), transparent 28%),
                radial-gradient(circle at 15% 10%, rgba(62, 108, 143, 0.05), transparent 22%),
                linear-gradient(180deg, #fbfcfe 0%, var(--bg) 100%);
        }
        .block-container {
            max-width: 1320px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        [data-testid="stHeader"] {
            background: #0f1218;
        }
        [data-testid="stHeader"] button,
        [data-testid="stHeader"] a,
        [data-testid="stHeader"] svg {
            color: #e8edf5 !important;
            fill: #e8edf5 !important;
        }
        [data-testid="stToolbar"] button,
        [data-testid="stToolbar"] a,
        [data-testid="stToolbar"] svg {
            color: #e8edf5 !important;
            fill: #e8edf5 !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: var(--heading) !important;
        }
        p, li, label, span {
            color: var(--text);
        }
        .hero-shell {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            background:
                radial-gradient(circle at top right, rgba(255,255,255,0.16), transparent 24%),
                linear-gradient(135deg, rgba(31, 92, 77, 0.98), rgba(33, 42, 38, 0.96));
            border-radius: 30px;
            padding: 1.9rem 1.95rem;
            margin-bottom: 1.35rem;
            color: #f7fffd;
            box-shadow: 0 28px 60px rgba(10, 32, 27, 0.18);
        }
        .hero-shell::after {
            content: "";
            position: absolute;
            inset: auto -10% -55% auto;
            width: 340px;
            height: 340px;
            background: radial-gradient(circle, rgba(255,255,255,0.18), rgba(255,255,255,0));
            pointer-events: none;
        }
        .hero-grid {
            display: grid;
            grid-template-columns: 1.6fr 1fr;
            gap: 1rem;
            align-items: stretch;
        }
        .hero-kicker {
            display: inline-block;
            font-size: 0.74rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: rgba(231, 255, 250, 0.75);
            margin-bottom: 0.7rem;
            font-weight: 700;
        }
        .hero-title {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 2.3rem;
            line-height: 1.05;
            margin: 0;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #f7fffd !important;
        }
        .hero-copy {
            max-width: 700px;
            margin: 0;
            color: rgba(238, 255, 251, 0.86);
            font-size: 1rem;
            line-height: 1.65;
        }
        .hero-stats {
            display: flex;
            gap: 0.8rem;
            margin-top: 1.15rem;
            flex-wrap: wrap;
        }
        .hero-stat {
            min-width: 132px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.10);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 0.9rem 1rem;
        }
        .hero-stat-label {
            font-size: 0.72rem;
            color: rgba(231, 255, 250, 0.72);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.3rem;
        }
        .hero-stat-value {
            font-size: 1.55rem;
            font-weight: 800;
            color: #ffffff;
        }
        .hero-status {
            border-radius: 22px;
            padding: 1.3rem 1.2rem;
            min-height: 100%;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.10);
            backdrop-filter: blur(10px);
        }
        .hero-status.idle {
            background: rgba(255,255,255,0.06);
        }
        .hero-status-label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(235, 255, 250, 0.72);
            margin-bottom: 0.45rem;
            font-weight: 700;
        }
        .hero-status-value {
            font-size: 1.35rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.4rem;
        }
        .hero-status-meta {
            color: rgba(238, 255, 251, 0.78);
            font-size: 0.95rem;
        }
        .section-card {
            border: 1px solid var(--line);
            background: var(--panel);
            border-radius: 26px;
            padding: 1.15rem 1.15rem 1.25rem;
            box-shadow: var(--shadow);
        }
        .section-title {
            font-family: Georgia, "Times New Roman", serif;
            margin: 0 0 0.25rem 0;
            font-size: 1.14rem;
            font-weight: 800;
            color: var(--text);
        }
        .section-copy {
            margin: 0 0 0.8rem 0;
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.6;
        }
        .mini-card-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin-top: 0.9rem;
        }
        .mini-card {
            border-radius: 22px;
            padding: 1rem;
            border: 1px solid var(--line);
            background: linear-gradient(180deg, #ffffff, #f7fbfa);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
        }
        .mini-card.vip {
            background: linear-gradient(180deg, rgba(15,118,110,0.10), rgba(255,255,255,0.98));
        }
        .mini-card.normal {
            background: linear-gradient(180deg, rgba(37,99,235,0.08), rgba(255,255,255,0.98));
        }
        .mini-card.fair {
            background: linear-gradient(180deg, rgba(245,158,11,0.10), rgba(255,255,255,0.98));
        }
        .mini-label {
            color: var(--muted);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.3rem;
        }
        .mini-value {
            color: var(--text);
            font-size: 1.55rem;
            font-weight: 800;
        }
        .mini-meta {
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: 0.2rem;
        }
        .queue-empty {
            border: 1px dashed var(--line);
            border-radius: 18px;
            padding: 1rem;
            color: var(--muted);
            background: rgba(255,255,255,0.55);
        }
        .fairness-note {
            margin-top: 0.8rem;
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.5;
        }
        .section-spacer {
            height: 0.9rem;
        }
        [data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(255,253,249,0.98), rgba(247,243,236,0.94));
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem;
            box-shadow: var(--shadow);
            min-height: 136px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        [data-testid="stMetricLabel"] {
            color: var(--tab-text) !important;
            font-weight: 700;
        }
        [data-testid="stMetricValue"] {
            color: var(--text);
            font-weight: 800;
        }
        [data-testid="stMetricDelta"] {
            color: var(--muted) !important;
        }
        [data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--line);
        }
        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(230, 242, 239, 0.98), rgba(214, 234, 229, 0.98));
            border-right: 1px solid rgba(15, 23, 42, 0.08);
        }
        [data-testid="stSidebar"] {
            color: var(--text);
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {
            color: var(--text);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding: 0.55rem 1rem;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(13, 39, 31, 0.08);
            color: var(--tab-text) !important;
            font-weight: 700;
        }
        .stTabs [data-baseweb="tab"] * {
            color: var(--tab-text) !important;
            fill: var(--tab-text) !important;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(31,92,77,0.10), rgba(62,108,143,0.12));
            color: var(--heading) !important;
        }
        .stTabs [aria-selected="true"] * {
            color: var(--heading) !important;
            fill: var(--heading) !important;
        }
        .stButton > button {
            border-radius: 16px;
            border: 1px solid #d0d7e2;
            padding: 0.78rem 1rem;
            font-weight: 700;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1f5c4d, #2f7d68);
            color: #ffffff;
        }
        .stButton > button[kind="primary"]:hover {
            border-color: rgba(11, 93, 86, 0.16);
            color: #ffffff;
        }
        .stButton > button[kind="primary"] *,
        .stButton > button[kind="primary"]:hover * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: #ffffff;
            color: var(--text);
        }
        [data-testid="stExpander"] {
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            background: rgba(255,255,255,0.95);
        }
        [data-testid="stExpander"] summary {
            color: var(--text) !important;
            font-weight: 700;
            background: #f3f6fb !important;
            border-bottom: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px 18px 0 0;
        }
        [data-testid="stExpander"] summary:hover {
            background: #eef2f8 !important;
        }
        [data-testid="stExpander"] summary svg {
            fill: var(--muted) !important;
            color: var(--muted) !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            line-height: 1.55;
        }
        [data-testid="stSidebar"] hr {
            margin: 0.6rem 0 0.5rem 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            margin-top: 0 !important;
            margin-bottom: 0.35rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stAlertContainer"] {
            margin-top: 0 !important;
        }
        .stTextInput input,
        .stTextInput div[data-baseweb="base-input"],
        .stSelectbox div[data-baseweb="select"] > div,
        .stMultiSelect div[data-baseweb="select"] > div,
        .stRadio > div {
            border-radius: 14px;
        }
        .stTextInput div[data-baseweb="base-input"] {
            background: var(--input-bg) !important;
            border: 2px solid #7ba7a2 !important;
            box-shadow: none !important;
            outline: none !important;
        }
        .stTextInput input {
            background: var(--input-bg) !important;
            color: var(--input-text) !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            border-radius: 14px !important;
            caret-color: #111111 !important;
        }
        .stTextInput input::placeholder {
            color: var(--input-placeholder) !important;
            opacity: 1;
        }
        .stTextInput input:focus,
        .stTextInput input:focus-visible {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }
        .stTextInput div[data-baseweb="base-input"]:focus-within,
        .stTextInput div[data-baseweb="base-input"]:focus,
        .stTextInput div[data-baseweb="base-input"]:focus-visible {
            border: 2px solid #5a8f88 !important;
            box-shadow: 0 0 0 2px rgba(63, 143, 127, 0.10) !important;
            outline: none !important;
        }
        .stTextInput > div,
        .stTextInput > div > div,
        .stTextInput > div > div > div {
            box-shadow: none !important;
        }
        .stSelectbox div[data-baseweb="select"] > div,
        .stMultiSelect div[data-baseweb="select"] > div {
            background: var(--input-bg) !important;
            color: var(--input-text) !important;
            border: 1px solid #c7d7d6 !important;
            box-shadow: none !important;
        }
        .stSelectbox div[data-baseweb="select"] > div:focus-within,
        .stMultiSelect div[data-baseweb="select"] > div:focus-within {
            border: 1px solid #7ba7a2 !important;
            box-shadow: 0 0 0 2px rgba(63, 143, 127, 0.10) !important;
        }
        .stSelectbox svg,
        .stMultiSelect svg {
            color: var(--muted) !important;
            fill: var(--muted) !important;
        }
        .stRadio label,
        .stRadio p {
            color: var(--text) !important;
        }
        .stRadio [role="radiogroup"] {
            background: #ffffff;
            border: 1px solid var(--input-border);
            border-radius: 14px;
            padding: 0.35rem 0.5rem;
        }
        .stInfo, .stWarning, .stSuccess {
            border-radius: 18px;
        }
        .stMarkdown h4 {
            color: var(--heading) !important;
            font-weight: 800 !important;
        }
        .stMarkdown p {
            color: var(--text) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-grid">
                <div>
                    <h1 class="hero-title">Call Center Waiting Line System</h1>
                    <div class="hero-stats">
                        <div class="hero-stat">
                            <div class="hero-stat-label">Total Waiting</div>
                            <div class="hero-stat-value">{total_waiting}</div>
                        </div>
                        <div class="hero-stat">
                            <div class="hero-stat-label">VIP Queue</div>
                            <div class="hero-stat-value">{vip_waiting}</div>
                        </div>
                        <div class="hero-stat">
                            <div class="hero-stat-label">Standard Queue</div>
                            <div class="hero-stat-value">{normal_waiting}</div>
                        </div>
                    </div>
                </div>
                <div>
                    {status_html}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def add_normal_call_callback():
    """Add a standard customer through the backend queue manager."""
    name = st.session_state.normal_name_input
    call_type = st.session_state.normal_type_input
    result = st.session_state.queue_manager.add_normal_customer(name, call_type)

    if result["success"]:
        st.toast(result["message"])
        st.session_state.normal_name_input = ""
    else:
        st.warning(result["message"])


def add_priority_call_callback():
    """Add a VIP customer through the backend queue manager."""
    name = st.session_state.vip_name_input
    vip_level = st.session_state.vip_level_input
    service_type = st.session_state.vip_type_input
    result = st.session_state.queue_manager.add_vip_customer(name, service_type, vip_level)

    if result["success"]:
        st.toast(result["message"])
        st.session_state.vip_name_input = ""
    else:
        st.warning(result["message"])


def serve_next_call_callback():
    """Serve next call using backend fairness logic."""
    result = st.session_state.queue_manager.serve_next_call()
    st.session_state.current_serving = result.get("current_serving")

    if not result["success"]:
        st.toast(result["message"])
        return

    if result["customer_type"] == "VIP":
        st.balloons()


def render_sidebar_inputs():
    """Build sidebar forms for standard and VIP customers."""
    with st.sidebar.expander("Standard Caller", expanded=True):
        st.text_input("Customer name", key="normal_name_input", placeholder="e.g. Nguyen Van A")
        st.selectbox("Service type", SERVICE_OPTIONS, key="normal_type_input")
        st.button("Add to standard queue", on_click=add_normal_call_callback, use_container_width=True)

    with st.sidebar.expander("VIP Caller", expanded=True):
        st.text_input("VIP customer name", key="vip_name_input", placeholder="e.g. Tran Thi B")
        st.selectbox("Service type", SERVICE_OPTIONS, key="vip_type_input")
        st.radio(
            "VIP tier",
            options=[30, 20, 10],
            format_func=lambda x: VIP_LABELS[x],
            key="vip_level_input",
        )
        st.button("Add to VIP queue", on_click=add_priority_call_callback, use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.caption("Fairness policy")
    st.sidebar.info(st.session_state.queue_manager.fairness_summary())


def render_dashboard_panels():
    """Render a polished operations summary above the action area."""
    queue_manager = st.session_state.queue_manager
    current = st.session_state.current_serving
    current_name = current["name"] if current else "No active call"
    current_meta = f"{current['type']} | {current['detail']}" if current else "Operator is ready"

    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown(
            f"""
            <div class="section-card">
                <div class="section-title">Operator Console</div>
                <div class="section-copy">One-click dispatch for the next caller, with VIP urgency and fairness handled in the backend.</div>
                <div class="mini-card-grid">
                    <div class="mini-card">
                        <div class="mini-label">Current Focus</div>
                        <div class="mini-value">{current_name}</div>
                        <div class="mini-meta">{current_meta}</div>
                    </div>
                    <div class="mini-card vip">
                        <div class="mini-label">VIP Streak Limit</div>
                        <div class="mini-value">{queue_manager.max_consecutive_vip}</div>
                        <div class="mini-meta">Maximum consecutive VIP calls before standard queue gets a turn</div>
                    </div>
                    <div class="mini-card fair">
                        <div class="mini-label">Fairness Threshold</div>
                        <div class="mini-value">{queue_manager.normal_wait_threshold_seconds}s</div>
                        <div class="mini-meta">Standard caller waiting threshold for priority protection</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Dispatch Notes</div>
                <div class="section-copy">Priority callers stay ahead, but the system protects standard callers from starvation. Add callers from the sidebar, then use the action button below to advance the queue.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dashboard_metrics():
    """Display queue counters and fairness summary from backend manager."""
    queue_manager = st.session_state.queue_manager
    normal_q_size = queue_manager.normal_queue.size()
    vip_q_size = queue_manager.get_vip_queue_size()
    total_waiting = queue_manager.get_total_waiting()

    m1, m2, m3 = st.columns(3)
    m1.metric(label="Total Waiting", value=total_waiting, delta=f"+{total_waiting}" if total_waiting > 0 else "Live")
    m2.metric(label="VIP Queue", value=vip_q_size, delta="Priority", delta_color="inverse")
    m3.metric(label="Standard Queue", value=normal_q_size, delta="FIFO")
    st.markdown(f"<div class='fairness-note'>{queue_manager.fairness_summary()}</div>", unsafe_allow_html=True)


def render_queue_monitor():
    """Display current VIP and normal waiting lists."""
    queue_manager = st.session_state.queue_manager
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### VIP Priority Queue")
        vip_table_data = queue_manager.get_vip_queue_snapshot()
        if vip_table_data:
            st.dataframe(vip_table_data, use_container_width=True, hide_index=True)
        else:
            st.markdown("<div class='queue-empty'>No VIP callers are waiting right now.</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("#### Standard FIFO Queue")
        normal_list = queue_manager.get_normal_queue_snapshot()
        if normal_list:
            formatted_normal = [
                {
                    "Position": f"#{customer['position']}",
                    "Customer": customer["name"],
                    "Service": customer["call_type"],
                    "Joined": customer["joined_at"].split(" ")[1],
                }
                for customer in normal_list
            ]
            st.dataframe(formatted_normal, use_container_width=True, hide_index=True)
        else:
            st.markdown("<div class='queue-empty'>No standard callers are waiting right now.</div>", unsafe_allow_html=True)
