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
    if "vip_call_counter" not in st.session_state:
        st.session_state.vip_call_counter = 0

# ===========================================================================
# 🔄 CÁC HÀM CALLBACK (XỬ LÝ SỰ KIỆN NÚT BẤM)
# ===========================================================================

def add_normal_call_callback():
    """Callback for adding standard call to queue."""
    name = st.session_state.normal_name_input
    call_type = st.session_state.normal_type_input
    
    if name and name.strip():
        result = add_customer(st.session_state.normal_queue, name, call_type)
        if result["success"]:
            st.toast(result["message"], icon="✅")
            st.session_state.normal_name_input = ""
        else:
            st.error(result["message"])
    else:
        st.warning("Vui lòng nhập tên khách hàng!")

def add_priority_call_callback():
    """Callback for adding VIP priority call to queue."""
    name = st.session_state.vip_name_input
    vip_level = st.session_state.vip_level_input
    service_type = st.session_state.vip_type_input
    
    level_mapping = {30: "VIP Bạch Kim", 20: "VIP Vàng", 10: "VIP Bạc"}
    vip_rank = level_mapping.get(vip_level, "VIP")
    call_type = f"{vip_rank} - {service_type}"

    if name and name.strip():
        st.session_state.vip_call_counter += 1
        call_id = str(st.session_state.vip_call_counter)
        new_call = Call(call_id=call_id, name=name.strip(), base_priority=vip_level, call_type=call_type)
        st.session_state.priority_queue.enqueue_priority(new_call)
        st.toast(f"Tiếp nhận cuộc gọi VIP từ: {name}", icon="✅")
        st.session_state.vip_name_input = ""
    else:
        st.warning("Vui lòng nhập tên khách hàng VIP!")

def serve_next_call_callback():
    """Main callback for call routing - applies aging algorithm and logs to database."""
    st.session_state.priority_queue.reorder()
    
    if not st.session_state.priority_queue.is_empty():
        served_call = st.session_state.priority_queue.dequeue()
        joined_at_str = served_call.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        
        insert_call(
            name=served_call.name,
            customer_type="VIP",
            call_type=served_call.call_type,
            joined_at=joined_at_str
        )
        
        st.session_state.current_serving = {
            "name": served_call.name,
            "type": "VIP",
            "detail": served_call.call_type,
            "time": datetime.now().strftime("%H:%M:%S")
        }
        st.balloons()
        
    elif not st.session_state.normal_queue.is_empty():
        served_customer = st.session_state.normal_queue.dequeue()
        joined_at_str = served_customer.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        
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
    else:
        st.session_state.current_serving = None
        st.toast("Không có cuộc gọi nào trong hàng đợi", icon="ℹ️")

def render_sidebar_inputs():
    """Build input forms for the application sidebar."""
    st.sidebar.header("Tiếp Nhận Cuộc Gọi")
    
    with st.sidebar.expander("Khách Hàng Thường", expanded=True):
        st.text_input("Tên khách hàng:", key="normal_name_input")
        st.selectbox("Loại dịch vụ:", [
            "Hỗ trợ kỹ thuật",
            "Thanh toán hóa đơn", 
            "Tư vấn sản phẩm",
            "Khiếu nại dịch vụ",
            "Cấp lại mật khẩu",
            "Yêu cầu bảo hiểm",
            "Đặt hàng mới",
            "Kiểm tra tài khoản",
            "Hủy dịch vụ",
            "Khác"
        ], key="normal_type_input")
        st.button("Thêm vào hàng", on_click=add_normal_call_callback, use_container_width=True)
        
    st.sidebar.markdown("---")
    
    with st.sidebar.expander("Khách Hàng VIP", expanded=True):
        st.text_input("Tên khách VIP:", key="vip_name_input")
        st.selectbox("Loại dịch vụ:", [
            "Hỗ trợ kỹ thuật",
            "Thanh toán hóa đơn", 
            "Tư vấn sản phẩm",
            "Khiếu nại dịch vụ",
            "Cấp lại mật khẩu",
            "Yêu cầu bảo hiểm",
            "Đặt hàng mới",
            "Kiểm tra tài khoản",
            "Hủy dịch vụ",
            "Khác"
        ], key="vip_type_input")
        st.radio(
            "Hạng VIP:", 
            options=[30, 20, 10], 
            format_func=lambda x: {30: "VIP Bạch Kim (Ưu tiên cao nhất)", 20: "VIP Vàng", 10: "VIP Bạc"}[x], 
            key="vip_level_input"
        )
        st.button("Thêm vào hàng ưu tiên", on_click=add_priority_call_callback, use_container_width=True)

def render_dashboard_metrics():
    """Display real-time queue statistics."""
    normal_q_size = st.session_state.normal_queue.size()
    
    vip_q_size = 0
    curr = st.session_state.priority_queue.head
    while curr is not None:
        vip_q_size += 1
        curr = curr.next
        
    total_waiting = normal_q_size + vip_q_size
    
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Tổng cuộc gọi chờ", value=total_waiting, delta=f"+{total_waiting}" if total_waiting > 0 else 0)
    m2.metric(label="Hàng VIP", value=vip_q_size, delta="Ưu tiên cao", delta_color="inverse")
    m3.metric(label="Hàng thường", value=normal_q_size)

def render_queue_monitor():
    """Display monitoring tables for both queue lines."""
    st.subheader("Giám Sát Hàng Đợi Thời Gian Thực")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Hàng Ưu Tiên VIP (Danh Sách Liên Kết)")
        vip_table_data = []
        
        curr = st.session_state.priority_queue.head
        while curr is not None:
            vip_table_data.append({
                "Vị Trí": f"#{curr.call_id}",
                "Tên Khách Hàng": curr.name,
                "Loại Dịch Vụ": curr.call_type,
                "Thời Gian Gọi": curr.joined_at.strftime("%H:%M:%S"),
                "Điểm Ưu Tiên": f"{curr.effective_score():.2f}"
            })
            curr = curr.next
            
        if vip_table_data:
            st.dataframe(vip_table_data, use_container_width=True, hide_index=True)
        else:
            st.caption("Không có cuộc gọi VIP trong hàng ưu tiên")
            
    with col2:
        st.markdown("#### Hàng Thường (FIFO)")
        normal_list = st.session_state.normal_queue.get_all()
        
        if normal_list:
            formatted_normal = [{
                "Vị Trí": f"#{c['position']}",
                "Tên Khách Hàng": c['name'],
                "Loại Dịch Vụ": c['call_type'],
                "Thời Gian Gọi": c['joined_at'].split(" ")[1]
            } for c in normal_list]
            st.dataframe(formatted_normal, use_container_width=True, hide_index=True)
        else:
            st.caption("Không có cuộc gọi nào trong hàng thường")