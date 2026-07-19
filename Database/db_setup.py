from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "call_center.db"


def create_tables() -> None:
    """Create tables for active queue state and handled call history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            customer_type TEXT NOT NULL,
            call_type TEXT NOT NULL,
            joined_at TEXT NOT NULL,
            served_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS active_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            customer_type TEXT NOT NULL,
            call_type TEXT NOT NULL,
            joined_at TEXT NOT NULL,
            vip_level INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    conn.commit()
    conn.close()


def add_active_call(
    name: str,
    customer_type: str,
    call_type: str,
    joined_at: str,
    vip_level: int = 0,
) -> int:
    """Persist a newly queued caller and return its database id."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO active_calls (name, customer_type, call_type, joined_at, vip_level)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, customer_type, call_type, joined_at, vip_level),
    )
    conn.commit()
    row_id = int(cursor.lastrowid)
    conn.close()
    return row_id


def get_active_calls() -> list[dict[str, Any]]:
    """Load currently waiting callers from SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, customer_type, call_type, joined_at, vip_level
        FROM active_calls
        ORDER BY id ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "name": row[1],
            "customer_type": row[2],
            "call_type": row[3],
            "joined_at": row[4],
            "vip_level": row[5],
        }
        for row in rows
    ]


def complete_active_call(
    call_id: int,
    name: str,
    customer_type: str,
    call_type: str,
    joined_at: str,
) -> None:
    """Move a caller from the active queue table into handled-call history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    served_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, customer_type, call_type, joined_at, served_at),
    )
    cursor.execute("DELETE FROM active_calls WHERE id = ?", (call_id,))
    conn.commit()
    conn.close()


def get_all_calls() -> pd.DataFrame:
    """Return handled-call history ordered by newest first."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM call_logs ORDER BY id DESC", conn)
    conn.close()
    return df


def seed_data() -> None:
    """Load sample history data when the history table is empty."""
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
        cursor.executemany(
            """
            INSERT INTO call_logs (name, customer_type, call_type, joined_at, served_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            sample_calls,
        )
        conn.commit()

    conn.close()


if __name__ == "__main__":
    create_tables()
    seed_data()
    print(get_all_calls().head(2))
