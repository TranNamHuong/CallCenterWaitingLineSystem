import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from Database.db_setup import get_all_calls

@st.cache_data(ttl=5)
def cached_get_all_calls():
    """Cache database calls for 5 seconds to improve performance."""
    return get_all_calls()

def render_analytics_dashboard():
    """Analyze historical data and display productivity statistics with Plotly."""
    st.subheader("Báo Cáo Thống Kê & Hiệu Suất")
    
    df = cached_get_all_calls()
    
    if df.empty:
        st.info("Cơ sở dữ liệu trống. Biểu đồ sẽ hiển thị khi có cuộc gọi được xử lý.")
        return
        
    total_handled = len(df)
    vip_count = len(df[df['customer_type'] == 'VIP'])
    standard_count = len(df[df['customer_type'].isin(['Standard', 'Thường'])])
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="Cuộc Gọi Đã Xử Lý", value=total_handled)
    kpi2.metric(label="Cuộc Gọi VIP", value=vip_count)
    kpi3.metric(label="Cuộc Gọi Thường", value=standard_count)
        
    st.markdown("---")
    
    # 2. Thiết lập layout chia đôi màn hình để vẽ 2 biểu đồ song song
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Phân Bố Theo Loại Khách Hàng")
        type_counts = df['customer_type'].value_counts().reset_index()
        type_counts.columns = ['Loại Khách Hàng', 'Số Cuộc Gọi']
        
        fig_types = px.bar(
            type_counts, 
            x='Loại Khách Hàng', 
            y='Số Cuộc Gọi',
            color='Loại Khách Hàng',
            color_discrete_map={'VIP': '#2E86AB', 'Standard': '#A23B72', 'Thường': '#A23B72'},
            text='Số Cuộc Gọi',
            title=None,
            template='plotly_white'
        )
        fig_types.update_traces(textposition='auto', hovertemplate='<b>%{x}</b><br>Số lượng: %{y}<extra></extra>')
        fig_types.update_layout(
            showlegend=False,
            height=400,
            font=dict(size=12),
            hovermode='closest'
        )
        fig_types.update_xaxes(title_text="")
        fig_types.update_yaxes(title_text="")
        st.plotly_chart(fig_types, use_container_width=True)
        
    with col2:
        st.markdown("### Tỷ Lệ Phân Bố Khách Hàng")
        fig_pie = px.pie(
            type_counts,
            values='Số Cuộc Gọi',
            names='Loại Khách Hàng',
            color='Loại Khách Hàng',
            color_discrete_map={'VIP': '#2E86AB', 'Standard': '#A23B72', 'Thường': '#A23B72'},
            template='plotly_white',
            hole=0.3
        )
        fig_pie.update_traces(
            hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<br>Tỷ lệ: %{percent}<extra></extra>',
            textposition='inside',
            textinfo='percent+label'
        )
        fig_pie.update_layout(
            height=400,
            font=dict(size=12),
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    
    st.markdown("### Phân Bố Cuộc Gọi Theo Dịch Vụ")
    df['clean_call_type'] = df['call_type'].apply(lambda x: x.split(" - ")[-1] if " - " in x else x)
    category_counts = df['clean_call_type'].value_counts().reset_index()
    category_counts.columns = ['Loại Dịch Vụ', 'Số Cuộc Gọi']
    
    fig_categories = px.bar(
        category_counts,
        y='Loại Dịch Vụ',
        x='Số Cuộc Gọi',
        orientation='h',
        color='Số Cuộc Gọi',
        color_continuous_scale='Viridis',
        text='Số Cuộc Gọi',
        template='plotly_white'
    )
    fig_categories.update_traces(textposition='auto', hovertemplate='<b>%{y}</b><br>Số lượng: %{x}<extra></extra>')
    fig_categories.update_layout(
        showlegend=False,
        height=400,
        font=dict(size=12),
        hovermode='closest'
    )
    fig_categories.update_xaxes(title_text="")
    fig_categories.update_yaxes(title_text="")
    st.plotly_chart(fig_categories, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("---")
    st.markdown("### Nhật Ký Lịch Sử Cuộc Gọi")
    display_df = df[['id', 'name', 'customer_type', 'call_type', 'joined_at', 'served_at']].copy()
    display_df.columns = ['Mã', 'Tên Khách Hàng', 'Loại', 'Dịch Vụ', 'Thời Gian Gọi Vào', 'Thời Gian Tiếp Nhận']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)