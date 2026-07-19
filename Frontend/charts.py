import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from Database.db_setup import get_all_calls


VIP_COLOR = "#1f5c4d"
STANDARD_COLOR = "#3e6c8f"
PLOT_BG = "rgba(255,255,255,0)"
PAPER_BG = "rgba(255,255,255,0)"
TEXT_COLOR = "#243447"
MUTED_TEXT_COLOR = "#526071"

SERVICE_TRANSLATIONS = {
    "Hỗ trợ kỹ thuật": "Technical Support",
    "Thanh toán hóa đơn": "Billing",
    "Thanh toán hoá đơn": "Billing",
    "Tư vấn sản phẩm": "Product Consultation",
    "Khiếu nại dịch vụ": "Service Complaint",
    "Khiếu nại": "Complaint",
    "Cấp lại mật khẩu": "Password Reset",
    "Yêu cầu bảo hiểm": "Insurance Request",
    "Đặt hàng mới": "New Order",
    "Kiểm tra tài khoản": "Account Check",
    "Hủy dịch vụ": "Service Cancellation",
    "Khác": "Other",
    "Giao dịch lớn": "Large Transaction",
    "Hỗ trợ khẩn cấp": "Emergency Support",
}

VIP_TRANSLATIONS = {
    "VIP Bạc": "Silver VIP",
    "VIP Vàng": "Gold VIP",
    "VIP Bạch Kim": "Platinum VIP",
    "Khách thường": "Standard",
    "Thường": "Standard",
}


@st.cache_data(ttl=5)
def cached_get_all_calls():
    """Cache database calls for 5 seconds to improve performance."""
    return get_all_calls()


def _chart_layout(title: str = "") -> dict:
    return {
        "title": {"text": title, "font": {"size": 18, "color": TEXT_COLOR}},
        "paper_bgcolor": PAPER_BG,
        "plot_bgcolor": PLOT_BG,
        "margin": {"l": 20, "r": 20, "t": 48, "b": 20},
        "font": {"family": "Segoe UI, Arial, sans-serif", "size": 12, "color": TEXT_COLOR},
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"color": TEXT_COLOR, "size": 12},
            "title": {"font": {"color": TEXT_COLOR, "size": 12}},
        },
        "coloraxis_colorbar": {
            "tickfont": {"color": TEXT_COLOR, "size": 12},
            "title": {"font": {"color": TEXT_COLOR, "size": 12}},
            "outlinecolor": "rgba(16,35,29,0.12)",
        },
    }


def _translate_service_label(value: str) -> str:
    normalized = value.strip()
    return SERVICE_TRANSLATIONS.get(normalized, normalized)


def _translate_call_type(value: str) -> str:
    if " - " in value:
        vip_label, service = value.split(" - ", 1)
        translated_vip = VIP_TRANSLATIONS.get(vip_label.strip(), vip_label.strip())
        translated_service = _translate_service_label(service)
        return f"{translated_vip} - {translated_service}"
    return _translate_service_label(value)


def _prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["customer_group"] = data["customer_type"].replace({"Thường": "Standard", "Thuong": "Standard"})
    data["customer_group"] = data["customer_group"].where(data["customer_group"] == "VIP", "Standard")
    data["call_type"] = data["call_type"].astype(str).apply(_translate_call_type)
    data["service_label"] = data["call_type"].apply(lambda x: x.split(" - ")[-1] if " - " in x else x)
    data["joined_dt"] = pd.to_datetime(data["joined_at"], errors="coerce")
    data["served_dt"] = pd.to_datetime(data["served_at"], errors="coerce")
    data["handle_minutes"] = (data["served_dt"] - data["joined_dt"]).dt.total_seconds().div(60).fillna(0)
    data["served_hour"] = data["served_dt"].dt.hour.fillna(0).astype(int)
    return data


def render_analytics_dashboard():
    """Analyze historical data and display polished operational analytics."""
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Operational Analytics</div>
            <div class="section-copy">Track volume, customer mix, service demand, and timing patterns from the call history database.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = cached_get_all_calls()
    if df.empty:
        st.info("No historical call data is available yet. Serve a few calls to unlock analytics.")
        return

    data = _prepare_dataframe(df)
    total_handled = len(data)
    vip_count = int((data["customer_group"] == "VIP").sum())
    standard_count = int((data["customer_group"] == "Standard").sum())
    avg_handle_minutes = round(data["handle_minutes"].mean(), 1)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Handled Calls", total_handled)
    k2.metric("VIP Calls", vip_count)
    k3.metric("Standard Calls", standard_count)
    k4.metric("Avg. Handling Time", f"{avg_handle_minutes} min")

    mix_counts = (
        data["customer_group"]
        .value_counts()
        .rename_axis("Customer Group")
        .reset_index(name="Calls")
    )
    service_counts = (
        data["service_label"]
        .value_counts()
        .rename_axis("Service")
        .reset_index(name="Calls")
        .sort_values("Calls", ascending=True)
    )
    hourly_counts = (
        data.groupby(["served_hour", "customer_group"])
        .size()
        .reset_index(name="Calls")
        .sort_values("served_hour")
    )

    col1, col2 = st.columns([1.05, 0.95])

    with col1:
        fig_mix = px.bar(
            mix_counts,
            x="Customer Group",
            y="Calls",
            color="Customer Group",
            text="Calls",
            color_discrete_map={"VIP": VIP_COLOR, "Standard": STANDARD_COLOR},
        )
        fig_mix.update_traces(
            textposition="outside",
            textfont={"color": TEXT_COLOR, "size": 13},
            hovertemplate="%{x}: %{y} calls<extra></extra>",
        )
        fig_mix.update_layout(**_chart_layout("Customer Mix"))
        fig_mix.update_xaxes(title="", tickfont={"color": TEXT_COLOR}, gridcolor="rgba(16,35,29,0.04)")
        fig_mix.update_yaxes(title="", tickfont={"color": TEXT_COLOR}, gridcolor="rgba(16,35,29,0.08)")
        st.plotly_chart(fig_mix, use_container_width=True)

    with col2:
        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=mix_counts["Customer Group"],
                    values=mix_counts["Calls"],
                    hole=0.62,
                    marker={"colors": [VIP_COLOR, STANDARD_COLOR]},
                    textinfo="label+percent",
                    textfont={"color": TEXT_COLOR, "size": 13},
                    hovertemplate="%{label}: %{value} calls (%{percent})<extra></extra>",
                )
            ]
        )
        fig_donut.update_layout(**_chart_layout("Queue Share"))
        st.plotly_chart(fig_donut, use_container_width=True)

    col3, col4 = st.columns([1.15, 0.85])

    with col3:
        fig_services = px.bar(
            service_counts,
            x="Calls",
            y="Service",
            orientation="h",
            color="Calls",
            color_continuous_scale=["#eee4cf", "#94b8ab", "#1f5c4d"],
            text="Calls",
        )
        fig_services.update_traces(
            textposition="outside",
            textfont={"color": TEXT_COLOR, "size": 13},
            hovertemplate="%{y}: %{x} calls<extra></extra>",
        )
        fig_services.update_layout(**_chart_layout("Service Demand"))
        fig_services.update_xaxes(title="", tickfont={"color": TEXT_COLOR}, gridcolor="rgba(16,35,29,0.08)")
        fig_services.update_yaxes(title="", tickfont={"color": TEXT_COLOR})
        st.plotly_chart(fig_services, use_container_width=True)

    with col4:
        top_service = service_counts.iloc[-1]["Service"]
        top_volume = int(service_counts.iloc[-1]["Calls"])
        vip_share = round((vip_count / total_handled) * 100, 1) if total_handled else 0
        st.markdown(
            f"""
            <div class="section-card">
                <div class="section-title">Quick Insight</div>
                <div class="section-copy">A compact summary for supervisors and operators.</div>
                <div class="mini-card-grid" style="grid-template-columns: 1fr;">
                    <div class="mini-card vip">
                        <div class="mini-label">Highest Demand Service</div>
                        <div class="mini-value">{top_service}</div>
                        <div class="mini-meta">{top_volume} calls recorded</div>
                    </div>
                    <div class="mini-card normal">
                        <div class="mini-label">VIP Share</div>
                        <div class="mini-value">{vip_share}%</div>
                        <div class="mini-meta">Portion of handled calls coming from VIP customers</div>
                    </div>
                    <div class="mini-card fair">
                        <div class="mini-label">Coverage Window</div>
                        <div class="mini-value">{data['served_dt'].dt.date.nunique()} days</div>
                        <div class="mini-meta">Unique calendar days represented in the current history</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    fig_hourly = px.area(
        hourly_counts,
        x="served_hour",
        y="Calls",
        color="customer_group",
        line_group="customer_group",
        color_discrete_map={"VIP": VIP_COLOR, "Standard": STANDARD_COLOR},
    )
    fig_hourly.update_traces(mode="lines+markers", hovertemplate="Hour %{x}: %{y} calls<extra></extra>")
    fig_hourly.update_layout(**_chart_layout("Handled Calls by Hour"))
    fig_hourly.update_xaxes(title="Hour of day", dtick=1, tickfont={"color": TEXT_COLOR}, title_font={"color": TEXT_COLOR}, gridcolor="rgba(16,35,29,0.08)")
    fig_hourly.update_yaxes(title="Calls", tickfont={"color": TEXT_COLOR}, title_font={"color": TEXT_COLOR}, gridcolor="rgba(16,35,29,0.08)")
    st.plotly_chart(fig_hourly, use_container_width=True)
