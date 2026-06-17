import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
from faker import Faker

DB_PATH = "call_center.db"
fake = Faker('vi_VN') # Vietnamese mock data

def create_tables() -> None:
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    served_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, customer_type, call_type, joined_at, served_at_str))
    conn.commit()
    conn.close()

def seed_data(num_records=50) -> None:
    """Generate random mock data for testing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM call_logs")
    
    if cursor.fetchone()[0] == 0:
        print(f"Generating {num_records} mock customers...")
        sample_calls = []
        services = ["Hỗ trợ kỹ thuật", "Thanh toán", "Khiếu nại", "Tư vấn sản phẩm"]
        types = ["VIP", "Standard"]
        
        for _ in range(num_records):
            name = fake.name()
            c_type = random.choices(types, weights=[30, 70])[0] # 30% VIP, 70% Standard
            service = random.choice(services)
            join_time = datetime.now() - timedelta(minutes=random.randint(5, 120))
            serve_time = join_time + timedelta(minutes=random.randint(2, 15))
            
            sample_calls.append((
                name, c_type, service, 
                join_time.strftime("%Y-%m-%d %H:%M:%S"),
                serve_time.strftime("%Y-%m-%d %H:%M:%S")
            ))
            
        cursor.executemany("""
            INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
            VALUES (?, ?, ?, ?, ?)
        """, sample_calls)
        conn.commit()
        print("Mock data loaded successfully!")
    
    conn.close()

if __name__ == "__main__":
    create_tables()
    seed_data()