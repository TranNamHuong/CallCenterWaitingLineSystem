import sqlite3
import pandas as pd
from datetime import datetime

# Đường dẫn cố định trỏ đến file dữ liệu nằm trong thư mục database/
DB_PATH = "Database/call_center.db"

def create_tables() -> None:
    """Tạo bảng lưu trữ lịch sử cuộc gọi nếu chưa tồn tại trong hệ thống."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tạo bảng call_logs với các trường dữ liệu cốt lõi phục vụ CSD203
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            customer_type TEXT NOT NULL,  -- 'VIP' hoặc 'Thường'
            call_type TEXT NOT NULL,      -- Chi tiết hạng dịch vụ hoặc lý do gọi
            joined_at TEXT NOT NULL,      -- Thời điểm khách bắt đầu vào hàng chờ
            served_at TEXT NOT NULL       -- Thời điểm tổng đài viên bấm nút tiếp nhận
        )
    """)
    conn.commit()
    conn.close()

def insert_call(name: str, customer_type: str, call_type: str, joined_at: str) -> None:
    """Ghi nhận và lưu trực tiếp lịch sử cuộc gọi xuống ổ cứng ngay khi tiếp nhận."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lấy thời gian thực tại thời điểm tổng đài viên bấm máy nghe cuộc gọi
    served_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, customer_type, call_type, joined_at, served_at_str))
    
    conn.commit()
    conn.close()

def get_all_calls() -> pd.DataFrame:
    """Truy xuất toàn bộ lịch sử cuộc gọi từ DB lên thành bảng dữ liệu Pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    
    # Sử dụng Pandas đọc SQL trực tiếp để xuất ra cấu trúc bảng cực nhanh
    query = "SELECT * FROM call_logs ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df

def seed_data() -> None:
    """Tự động bơm dữ liệu lịch sử mẫu để vẽ biểu đồ thống kê nếu DB đang trống."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Kiểm tra xem bảng đã có dữ liệu tích lũy từ trước hay chưa
    cursor.execute("SELECT COUNT(*) FROM call_logs")
    count = cursor.fetchone()[0]
    
    # Nếu chưa có dòng nào, tiến hành nạp dữ liệu giả lập có sẵn để chạy demo
    if count == 0:
        sample_calls = [
            ("Nguyễn Trần Khánh VIP", "VIP", "💎 Diamond VIP - Hỗ trợ khẩn cấp", "2026-06-03 08:15:00", "2026-06-03 08:16:30"),
            ("Lê Văn Nam", "Thường", "Thanh toán hoá đơn", "2026-06-03 08:20:00", "2026-06-03 08:25:00"),
            ("Phạm Minh Hoàng VIP", "VIP", "🥇 Gold VIP - Giao dịch lớn", "2026-06-03 09:05:00", "2026-06-03 09:07:00"),
            ("Trần Thị Bình", "Thường", "Tư vấn sản phẩm", "2026-06-03 09:11:00", "2026-06-03 09:18:00"),
            ("Đỗ Quốc Dũng", "Thường", "Hỗ trợ kỹ thuật", "2026-06-03 10:00:00", "2026-06-03 10:04:00"),
            ("Hoàng Diệu Thuý VIP", "VIP", "🥈 Silver VIP - Khiếu nại", "2026-06-03 10:30:00", "2026-06-03 10:32:00")
        ]
        
        cursor.executemany("""
            INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
            VALUES (?, ?, ?, ?, ?)
        """, sample_calls)
        
        conn.commit()
        print("🎉 Đã nạp thành công dữ liệu mẫu vào lịch sử!")
    
    conn.close()

# Đoạn mã kiểm tra nhanh độc lập khi chạy trực tiếp file database này
if __name__ == "__main__":
    import os
    print("--- Khởi tạo và thử nghiệm hệ thống dữ liệu SQLite ---")
    create_tables()
    seed_data()
    if os.path.exists(DB_PATH):
        print(f"✅ Thành công: File '{DB_PATH}' đã xuất hiện trên ổ cứng!")
        print(get_all_calls().head(2))