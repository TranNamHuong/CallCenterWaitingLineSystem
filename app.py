import streamlit as st
from Database.db_setup import create_tables, seed_data
from Frontend.UI_components import init_session_state, render_sidebar_inputs, render_dashboard_metrics, render_queue_monitor, serve_next_call_callback
from Frontend.charts import render_analytics_dashboard


# ===========================================================================
# 1. CẤU HÌNH TRANG WEB ĐỒ HỌA CAO CẤP
# ===========================================================================
st.set_page_config(
    page_title="Hệ Thống Xếp Hàng Call Center - CSD203",
    page_icon="☎",
    layout="wide"
)

# ===========================================================================
# 2. KHỞI TẠO NỀN TẢNG (DATABASE & SESSION STATE)
# ===========================================================================
# Tự động đẻ file call_center.db và nạp 6 cuộc gọi mẫu nếu mới chạy lần đầu
create_tables()
seed_data()

# Khởi tạo hàng đợi RAM lưu trữ danh sách khách chờ
init_session_state()

# ===========================================================================
# 3. DỰNG LAYOUT CHÍNH CHO PHẦN MỀM
# ===========================================================================
st.title("Hệ Thống Xếp Hàng Tổng Đài")
st.markdown("---")

# Gọi thanh công cụ nhập liệu xuất hiện ở bên hành lang trái màn hình (Sidebar)
render_sidebar_inputs()

# Chia màn hình chính thành 2 Tab chức năng cực kỳ hiện đại và mượt mà
tab_dashboard, tab_analytics = st.tabs(["Bàn Điều Phối", "Thống Kê & Biểu Đồ"])

# ---------------------------------------------------------------------------
# TAB 1: KHÔNG GIAN LÀM VIỆC CỦA TỔNG ĐÀI VIÊN
# ---------------------------------------------------------------------------
with tab_dashboard:
    st.markdown("### Bàn Làm Việc Tổng Đài Viên")
    
    if st.session_state.current_serving:
        cs = st.session_state.current_serving
        customer_type = "[VIP]" if cs["type"] == "VIP" else "[Thường]"
        st.success(
            f"**ĐANG TRONG CUỘC GỌI:** {cs['name']} | "
            f"**Loại:** {customer_type} | "
            f"**Dịch vụ:** {cs['detail']} | "
            f"**Lúc:** {cs['time']}"
        )
    else:
        st.info("Trạng thái: Rảnh tay. Nhấn nút dưới để tiếp nhận cuộc gọi tiếp theo.")
        
    st.button(
        "TIẾP NHẬN CUỘC GỌI TIẾP THEO", 
        on_click=serve_next_call_callback, 
        type="primary", 
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Gọi hàm hiển thị 3 thẻ chỉ số Metric (Tổng chờ, chờ VIP, chờ Thường)
    render_dashboard_metrics()
    
    st.markdown("---")
    
    render_queue_monitor()

with tab_analytics:
    render_analytics_dashboard()