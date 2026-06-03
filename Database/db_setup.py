import sqlite3
import pandas as pd
from datetime import datetime

# Đường dẫn cố định trỏ đến file dữ liệu nằm trong thư mục database/
DB_PATH = "Database/call_center.db"

def create_tables() -> None:
    """Create call history tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            customer_type TEXT NOT NULL,
            call_type TEXT NOT NULL,
            joined_at TEXT NOT NULL,
            served_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_call(name: str, customer_type: str, call_type: str, joined_at: str) -> None:
    """Log and save call history to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    served_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, customer_type, call_type, joined_at, served_at_str))
    
    conn.commit()
    conn.close()

def get_all_calls() -> pd.DataFrame:
    """Retrieve all call history from database as Pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    
    query = "SELECT * FROM call_logs ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df

def seed_data() -> None:
    """Auto-load sample data for demo if database is empty."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM call_logs")
    count = cursor.fetchone()[0]
    
    # Nếu chưa có dòng nào, tiến hành nạp dữ liệu giả lập có sẵn để chạy demo
    if count == 0:
        sample_calls = [
            ("Nguyen Van A", "VIP", "Platinum VIP - Technical Support", "2026-06-03 08:15:00", "2026-06-03 08:16:30"),
            ("Le Thi B", "Standard", "Billing", "2026-06-03 08:20:00", "2026-06-03 08:25:00"),
            ("Pham Minh C", "VIP", "Gold VIP - Product Info", "2026-06-03 09:05:00", "2026-06-03 09:07:00"),
            ("Tran Quoc D", "Standard", "Technical Support", "2026-06-03 09:11:00", "2026-06-03 09:18:00"),
            ("Hoang Duc E", "Standard", "Complaints", "2026-06-03 10:00:00", "2026-06-03 10:04:00"),
            ("Dinh Thi F", "VIP", "Silver VIP - Billing", "2026-06-03 10:30:00", "2026-06-03 10:32:00")
        ]
        
        cursor.executemany("""
            INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
            VALUES (?, ?, ?, ?, ?)
        """, sample_calls)
        
        conn.commit()
        print("Sample data loaded successfully!")
    
    conn.close()

# Quick test when running this file directly
if __name__ == "__main__":
    import os
    print("--- Initialize SQLite Database System ---")
    create_tables()
    seed_data()
    if os.path.exists(DB_PATH):
        print(f"Success: Database file '{DB_PATH}' created!")
        print(get_all_calls().head(2))