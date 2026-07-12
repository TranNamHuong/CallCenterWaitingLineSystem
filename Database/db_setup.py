import sqlite3
import os
from datetime import datetime
import pandas as pd

# Flat structure: db file lives next to this script, not in a "Database/" subfolder.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "call_center.db")


def create_tables() -> None:
    try:
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waiting_queue (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                customer_type TEXT NOT NULL CHECK (customer_type IN ('VIP', 'Standard')),
                call_type TEXT NOT NULL,
                base_priority INTEGER,
                joined_at TEXT NOT NULL
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        # Re-raise as a clear startup failure rather than letting FastAPI crash silently
        raise RuntimeError(f"Failed to create database tables: {e}") from e
    finally:
        conn.close()


def insert_call(name: str, customer_type: str, call_type: str, joined_at: str) -> bool:
    """Returns True/False instead of raising, so a DB write failure never
    takes down a request that has already dequeued a customer."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        served_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, customer_type, call_type, joined_at, served_at_str))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_call failed for '{name}': {e}")
        return False
    finally:
        conn.close()


def get_all_calls() -> pd.DataFrame:
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM call_logs ORDER BY id DESC", conn)
        return df
    except sqlite3.Error as e:
        print(f"[DB ERROR] get_all_calls failed: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def seed_data() -> None:
    """Loads placeholder demo rows ONLY if the table is empty.
    Replace `sample_calls` with your real dataset ingestion (e.g. pd.read_csv(...).itertuples())
    once you have an actual customer dataset file to load from."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM call_logs")
        count = cursor.fetchone()[0]

        if count == 0:
            sample_calls = [
                ("Nguyen Van A", "VIP", "Platinum VIP - Technical Support", "2026-06-03 08:15:00", "2026-06-03 08:16:30"),
                ("Le Thi B", "Standard", "Billing", "2026-06-03 08:20:00", "2026-06-03 08:25:00"),
                ("Pham Minh C", "VIP", "Gold VIP - Product Info", "2026-06-03 09:05:00", "2026-06-03 09:07:00"),
                ("Tran Quoc D", "Standard", "Technical Support", "2026-06-03 09:11:00", "2026-06-03 09:18:00"),
                ("Hoang Duc E", "Standard", "Complaints", "2026-06-03 10:00:00", "2026-06-03 10:04:00"),
                ("Dinh Thi F", "VIP", "Silver VIP - Billing", "2026-06-03 10:30:00", "2026-06-03 10:32:00"),
            ]
            cursor.executemany("""
                INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
                VALUES (?, ?, ?, ?, ?)
            """, sample_calls)
            conn.commit()
            print("Sample data loaded successfully!")
    except sqlite3.Error as e:
        print(f"[DB ERROR] seed_data failed: {e}")
    finally:
        conn.close()

def insert_waiting(id_: str, name: str, customer_type: str, call_type: str,
                    joined_at: str, base_priority: int = None) -> bool:
    """Lưu khách đang chờ xuống DB — dùng khi enqueue, để khôi phục nếu server restart."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO waiting_queue (id, name, customer_type, call_type, base_priority, joined_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_, name, customer_type, call_type, base_priority, joined_at))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_waiting failed for '{name}': {e}")
        return False
    finally:
        conn.close()


def delete_waiting(id_: str) -> bool:
    """Xóa khách khỏi bảng waiting_queue — dùng khi khách được serve hoặc bị remove."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM waiting_queue WHERE id = ?", (id_,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] delete_waiting failed for id '{id_}': {e}")
        return False
    finally:
        conn.close()


def get_all_waiting() -> list[dict]:
    """Đọc toàn bộ khách đang chờ, sắp theo thời gian vào trước — dùng lúc khởi động server."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM waiting_queue ORDER BY joined_at ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"[DB ERROR] get_all_waiting failed: {e}")
        return []
    finally:
        conn.close()




if __name__ == "__main__":
    print("--- Initialize SQLite Database System ---")
    create_tables()
    seed_data()
    if os.path.exists(DB_PATH):
        print(f"Success: Database file '{DB_PATH}' created!")
        print(get_all_calls().head(2))