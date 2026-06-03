import streamlit as st
from Database.db_setup import create_tables, seed_data
from Frontend.UI_components import init_session_state, render_sidebar_inputs, render_dashboard_metrics, render_queue_monitor, serve_next_call_callback
from Frontend.charts import render_analytics_dashboard

# ===========================================================================
# 1. CẤU HÌNH TRANG WEB ĐỒ HỌA CAO CẤP
# ===========================================================================
st.set_page_config(
    page_title="Hệ Thống Xếp Hàng Call Center - CSD203",
    page_icon="📞",
    layout="wide"  # Ép giao diện tràn màn hình ngang xem cho sướng mắt
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
st.title("📞 Hệ Thống Điều Phối & Xếp Hàng Chờ Call Center")
st.markdown("*Đồ án thực hành chuyên sâu môn Cấu trúc dữ liệu và Giải thuật (CSD203) - Nhóm Cộng Tác Viên*")
st.markdown("---")

# Gọi thanh công cụ nhập liệu xuất hiện ở bên hành lang trái màn hình (Sidebar)
render_sidebar_inputs()

# Chia màn hình chính thành 2 Tab chức năng cực kỳ hiện đại và mượt mà
tab_dashboard, tab_analytics = st.tabs(["🖥️ Màn Hình Điều Phối Tổng Đài", "📊 Biểu Đồ & Thống Kê Lịch Sử"])

# ---------------------------------------------------------------------------
# TAB 1: KHÔNG GIAN LÀM VIỆC CỦA TỔNG ĐÀI VIÊN
# ---------------------------------------------------------------------------
with tab_dashboard:
    st.markdown("### 🎧 Bàn Làm Việc Điều Phối Cuộc Gọi")
    
    # Khối hiển thị thông tin cuộc gọi đang kết nối thời gian thực
    if st.session_state.current_serving:
        cs = st.session_state.current_serving
        icon = "🔥 VIP" if cs["type"] == "VIP" else "👤 Thường"
        st.success(
            f"**🎧 ĐANG TRONG CUỘC GỌI:** {cs['name']} | "
            f"**Phân loại:** {icon} | "
            f"**Nội dung hỗ trợ:** {cs['detail']} | "
            f"**Kết nối lúc:** {cs['time']}"
        )
    else:
        st.info("ℹ️ Trạng thái: Tổng đài viên đang rảnh tay. Vui lòng nhấn nút to màu xanh phía dưới để bốc cuộc gọi tiếp theo ra xử lý.")
        
    # Nút bấm quyền lực nhất ứng dụng: Phục vụ khách hàng tiếp theo
    # Nút này bấm một cái là Callback kích hoạt: bốc khách khỏi Queue -> Lưu thẳng vào SQL Database!
    st.button(
        "🎧 TIẾP NHẬN CUỘC GỌI TIẾP THEO (ƯU TIÊN TUYẾN VIP / AGING PROCESS)", 
        on_click=serve_next_call_callback, 
        type="primary", 
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Gọi hàm hiển thị 3 thẻ chỉ số Metric (Tổng chờ, chờ VIP, chờ Thường)
    render_dashboard_metrics()
    
    st.markdown("---")
    
    # Gọi hàm hiển thị bảng giám sát so sánh 2 hàng chờ real-time
    render_queue_monitor()

# ---------------------------------------------------------------------------
# TAB 2: TRANG PHÂN TÍCH VÀ ĐỒ THỊ LỊCH SỬ
# ---------------------------------------------------------------------------
with tab_analytics:
    # Gọi toàn bộ cụm chức năng vẽ biểu đồ từ file charts.py lên màn hình
    render_analytics_dashboard()