import streamlit as st
import uuid
from datetime import datetime


from Backend.Normal_Queue import NormalQueue, Customer, add_customer
from Backend.priority_queue_logic import PriorityQueue, Call

# Import hàm ghi dữ liệu từ lớp Database
from Database.db_setup import insert_call

def init_session_state():
    """Khởi tạo và giữ cấu trúc hàng đợi cố định trong bộ nhớ RAM khi chạy Web application."""
    if "normal_queue" not in st.session_state:
        st.session_state.normal_queue = NormalQueue(max_size=50)
    if "priority_queue" not in st.session_state:
        st.session_state.priority_queue = PriorityQueue()
    if "current_serving" not in st.session_state:
        st.session_state.current_serving = None

# ===========================================================================
# 🔄 CÁC HÀM CALLBACK (XỬ LÝ SỰ KIỆN NÚT BẤM)
# ===========================================================================

def add_normal_call_callback():
    """Hàm Callback chạy khi người dùng nhấn nút 'Xếp hàng chờ (FIFO)'."""
    name = st.session_state.normal_name_input
    call_type = st.session_state.normal_type_input
    
    if name and name.strip():
        # Gọi hàm tiện ích của queue_logic để nhét khách thường vào hàng đợi deque
        result = add_customer(st.session_state.normal_queue, name, call_type)
        if result["success"]:
            st.toast(result["message"], icon="✅")
            st.session_state.normal_name_input = ""  # Reset ô nhập liệu
        else:
            st.error(result["message"])
    else:
        st.warning("⚠️ Vui lòng điền tên khách hàng thông thường!")

def add_priority_call_callback():
    """Hàm Callback chạy khi người dùng nhấn nút 'Chen hàng ưu tiên'."""
    name = st.session_state.vip_name_input
    vip_level = st.session_state.vip_level_input
    
    # Quy đổi điểm số ưu tiên gốc thành tên hạng thẻ để lưu vào hệ thống
    level_mapping = {30: "💎 Diamond VIP", 20: "🥇 Gold VIP", 10: "🥈 Silver VIP"}
    call_type = level_mapping.get(vip_level, "⭐ VIP")

    if name and name.strip():
        # Tạo mã ID cuộc gọi ngẫu nhiên (8 ký tự)
        call_id = str(uuid.uuid4())[:8]
        
        # Khởi tạo một Node Call mới dành cho Danh sách liên kết đơn
        new_call = Call(call_id=call_id, name=name.strip(), base_priority=vip_level, call_type=call_type)
        
        # Đẩy Node Call này vào hàng đợi ưu tiên Linked List ở Backend
        st.session_state.priority_queue.enqueue_priority(new_call)
        st.toast(f"👑 Đã tiếp nhận cuộc gọi ưu tiên từ khách VIP: '{name}'!", icon="👑")
        st.session_state.vip_name_input = ""  # Reset ô nhập liệu
    else:
        st.warning("⚠️ Vui lòng điền tên khách hàng VIP!")

def serve_next_call_callback():
    """Hàm Callback trung tâm: Phân luồng điều phối cuộc gọi và GHI TRỰC TIẾP VÀO DATABASE SQLite."""
    # BƯỚC QUAN TRỌNG: Kích hoạt thuật toán Reorder sắp xếp lại danh sách liên kết theo điểm Aging thực tế
    st.session_state.priority_queue.reorder()
    
    # Kịch bản 1: Tuyến ưu tiên VIP đang có người đứng đợi
    if not st.session_state.priority_queue.is_empty():
        # Bốc cuộc gọi lớn nhất đứng đầu danh sách liên kết ra phục vụ (O(1))
        served_call = st.session_state.priority_queue.dequeue()
        
        # Định dạng thời gian gọi vào chuẩn văn bản
        joined_at_str = served_call.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        
        # 💾 CHỐT HẠ: Gọi hàm của Database ghi thẳng lịch sử cuộc gọi VIP xuống ổ cứng ngay khi bốc máy
        insert_call(
            name=served_call.name,
            customer_type="VIP",
            call_type=served_call.call_type,
            joined_at=joined_at_str
        )
        
        # Lưu thông tin người đang nói chuyện lên màn hình chính
        st.session_state.current_serving = {
            "name": served_call.name,
            "type": "VIP",
            "detail": served_call.call_type,
            "time": datetime.now().strftime("%H:%M:%S")
        }
        st.balloons()  # Bắn bóng bay ăn mừng phục vụ VIP xuất sắc
        
    # Kịch bản 2: Tuyến VIP trống -> Tiến hành bốc tuyến khách thường theo luật FIFO
    elif not st.session_state.normal_queue.is_empty():
        # Bốc phần tử đầu tiên ra khỏi hàng đợi deque (O(1))
        served_customer = st.session_state.normal_queue.dequeue()
        
        # Định dạng thời gian gọi vào
        joined_at_str = served_customer.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        
        # 💾 CHỐT HẠ: Gọi hàm của Database ghi thẳng lịch sử cuộc gọi thông thường xuống ổ cứng
        insert_call(
            name=served_customer.name,
            customer_type="Thường",
            call_type=served_customer.call_type,
            joined_at=joined_at_str
        )
        
        st.session_state.current_serving = {
            "name": served_customer.name,
            "type": "Thường",
            "detail": served_customer.call_type,
            "time": datetime.now().strftime("%H:%M:%S")
        }
    # Kịch bản 3: Cả hai tuyến đều trống không còn ai chờ
    else:
        st.session_state.current_serving = None
        st.toast("Hiện tại tổng đài không còn cuộc gọi nào đang chờ xử lý!", icon="ℹ️")

# ===========================================================================
# 🎨 GIAO DIỆN HIỂN THỊ (LAYOUT COMPONENTS)
# ===========================================================================

def render_sidebar_inputs():
    """Xây dựng thanh nhập liệu chuyên nghiệp nằm ở bên hành lang trái màn hình."""
    st.sidebar.header("📞 Tiếp Nhận Cuộc Gọi Mới")
    
    # Form nhập liệu dành cho tuyến khách thông thường
    with st.sidebar.expander("👤 Khách Hàng Thông Thường", expanded=True):
        st.text_input("Tên khách hàng thường:", key="normal_name_input")
        st.selectbox("Dịch vụ yêu cầu:", ["Hỗ trợ kỹ thuật", "Thanh toán hoá đơn", "Tư vấn sản phẩm", "Khiếu nại dịch vụ"], key="normal_type_input")
        st.button("Xếp hàng chờ (FIFO)", on_click=add_normal_call_callback, use_container_width=True)
        
    st.sidebar.markdown("---")
    
    # Form nhập liệu dành cho tuyến khách hàng đặc quyền VIP
    with st.sidebar.expander("👑 Khách Hàng VIP Ưu Tiên", expanded=True):
        st.text_input("Tên khách VIP:", key="vip_name_input")
        st.radio(
            "Phân loại hạng thẻ VIP:", 
            options=[30, 20, 10], 
            format_func=lambda x: {30: "Diamond VIP (Ưu tiên nhất)", 20: "Gold VIP", 10: "Silver VIP"}[x], 
            key="vip_level_input"
        )
        st.button("Chen hàng ưu tiên", on_click=add_priority_call_callback, use_container_width=True)

def render_dashboard_metrics():
    """Hiển thị các khối chỉ số đếm số lượng người chờ thời gian thực ở đầu trang."""
    normal_q_size = st.session_state.normal_queue.size()
    
    # Đếm số lượng khách VIP hiện tại bằng cách duyệt thủ công danh sách liên kết đơn
    vip_q_size = 0
    curr = st.session_state.priority_queue.head
    while curr is not None:
        vip_q_size += 1
        curr = curr.next
        
    total_waiting = normal_q_size + vip_q_size
    
    # Đổ dữ liệu ra 3 cột chỉ số thông minh st.metric
    m1, m2, m3 = st.columns(3)
    m1.metric(label="📊 Tổng Cuộc Gọi Đang Chờ", value=total_waiting, delta=f"+{total_waiting}" if total_waiting > 0 else 0)
    m2.metric(label="💎 Tuyến VIP Đang Đợi", value=vip_q_size, delta="Độ ưu tiên cao", delta_color="inverse")
    m3.metric(label="👤 Tuyến Thường Đang Đợi", value=normal_q_size)

def render_queue_monitor():
    """Dựng hai bảng lưới DataFrame giám sát chi tiết thứ tự xếp hàng của 2 tuyến."""
    st.subheader("🖥️ Bảng Giám Sát Điều Phối Cuộc Gọi Real-time")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👑 Tuyến Ưu Tiên VIP (Linked List - Sorted By Aging)")
        vip_table_data = []
        
        # Duyệt dọc con trỏ danh sách liên kết để lấy dữ liệu Node hiển thị ra bảng đồ họa
        curr = st.session_state.priority_queue.head
        while curr is not None:
            vip_table_data.append({
                "ID Cuộc Gọi": curr.call_id,
                "Tên Khách VIP": curr.name,
                "Hạng Mục": curr.call_type,
                "Điểm Ưu Tiên Động": f"{curr.effective_score():.2f}"  # In điểm thực tế có lẻ giây Aging
            })
            curr = curr.next
            
        if vip_table_data:
            st.dataframe(vip_table_data, use_container_width=True, hide_index=True)
        else:
            st.caption("Chưa có cuộc gọi VIP nào trong tuyến chờ ưu tiên.")
            
    with col2:
        st.markdown("#### 👤 Tuyến Thông Thường (Standard FIFO Queue)")
        normal_list = st.session_state.normal_queue.get_all()
        
        if normal_list:
            # Format định dạng mảng dict từ queue_logic sang giao diện người dùng
            formatted_normal = [{
                "Vị Trí Chờ": f"#{c['position']}",
                "Tên Khách Hàng": c['name'],
                "Vấn Đề Hỗ Trợ": c['call_type'],
                "Thời Gian Gọi Vào": c['joined_at'].split(" ")[1]
            } for c in normal_list]
            st.dataframe(formatted_normal, use_container_width=True, hide_index=True)
        else:
            st.caption("Chưa có cuộc gọi thông thường nào trong tuyến chờ FIFO.")