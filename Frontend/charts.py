import streamlit as st
import pandas as pd
from Database.db_setup import get_all_calls

def render_analytics_dashboard():
    """Đọc dữ liệu lịch sử từ database và vẽ biểu đồ thống kê năng suất."""
    st.subheader("📊 Trung Tâm Phân Tích & Thống Kê Báo Cáo")
    
    # Đọc dữ liệu từ file call_center.db lên thành Pandas DataFrame
    df = get_all_calls()
    
    # Trường hợp Database trống (Chưa có cuộc gọi nào được xử lý xong)
    if df.empty:
        st.info("ℹ️ Hiện tại cơ sở dữ liệu lịch sử đang trống. Biểu đồ sẽ tự động hiển thị và cập nhật thời gian thực ngay khi cuộc gọi đầu tiên được tổng đài viên tiếp nhận!")
        return
        
    # 1. Tính toán các chỉ số nhanh (KPIs)
    total_handled = len(df)
    vip_count = len(df[df['customer_type'] == 'VIP'])
    normal_count = len(df[df['customer_type'] == 'Thường'])
    
    # Hiển thị các thẻ chỉ số thông minh ở hàng đầu tiên của trang thống kê
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="✅ Tổng Cuộc Gọi Đã Xử Lý", value=total_handled)
    kpi2.metric(label="💎 Tổng Lượt Khách VIP", value=vip_count)
    kpi3.metric(label="👤 Tổng Lượt Khách Thường", value=normal_count)
        
    st.markdown("---")
    
    # 2. Thiết lập layout chia đôi màn hình để vẽ 2 biểu đồ song song
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Thống kê theo Loại Khách Hàng")
        # Nhóm dữ liệu và đếm số lượng cuộc gọi theo phân loại (VIP/Thường)
        type_counts = df['customer_type'].value_counts().reset_index()
        type_counts.columns = ['Phân Loại', 'Số Lượng cuộc gọi']
        
        # Vẽ biểu đồ cột trực quan bằng hàm gốc của Streamlit
        st.bar_chart(data=type_counts, x='Phân Loại', y='Số Lượng cuộc gọi', color='Phân Loại')
        
    with col2:
        st.markdown("### 🛠️ Thống kê theo Danh Mục Hỗ Trợ")
        # Chuẩn hóa lại tên dịch vụ (bỏ tiền tố Diamond/Gold để gom nhóm chuẩn danh mục)
        df['clean_call_type'] = df['call_type'].apply(lambda x: x.split(" - ")[-1] if " - " in x else x)
        category_counts = df['clean_call_type'].value_counts().reset_index()
        category_counts.columns = ['Danh Mục Dịch Vụ', 'Số Cuộc Gọi']
        
        # Vẽ biểu đồ cột danh mục hỗ trợ
        st.bar_chart(data=category_counts, x='Danh Mục Dịch Vụ', y='Số Cuộc Gọi')
        
    st.markdown("---")
    
    # 3. Hiển thị bảng dữ liệu nhật ký chi tiết dạng Excel ở cuối trang
    st.markdown("### 🕒 Nhật Ký Chi Tiết Lịch Sử Cuộc Gọi")
    display_df = df[['id', 'name', 'customer_type', 'call_type', 'joined_at', 'served_at']].copy()
    display_df.columns = ['Mã Số', 'Tên Khách Hàng', 'Phân Loại', 'Dịch Vụ Hỗ Trợ', 'Thời Gian Gọi', 'Thời Gian Tiếp Nhận']
    
    # Hiện bảng dữ liệu, ẩn cột index mặc định của pandas cho đẹp giao diện
    st.dataframe(display_df, use_container_width=True, hide_index=True)