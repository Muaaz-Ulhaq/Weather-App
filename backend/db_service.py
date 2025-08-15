import sqlite3
from contextlib import contextmanager
from backend.config import DB_PATH, TABLE_NAME
import json
@contextmanager
def get_connection():
    """Context manager for SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def create_table():
    with get_connection() as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                date_from TEXT,
                date_to TEXT,
                data TEXT
            )
        """)

def create_record(record):
    with get_connection() as conn:
        cursor = conn.execute(
            f"""
            INSERT INTO {TABLE_NAME} (city, date_from, date_to, data)
            VALUES (?, ?, ?, ?)
            """,
            (record.city, record.date_from, record.date_to, record.data)
        )
        return {"id": cursor.lastrowid}

def get_all_records():
    with get_connection() as conn:
        #conn.execute(f"DROP TABLE IF EXISTS history")
        rows = conn.execute(f"SELECT * FROM {TABLE_NAME}").fetchall()
        columns = ["id", "city", "date_from", "date_to", "data"]
        return [dict(zip(columns, row)) for row in rows]

def delete_record(record_id: int):
    with get_connection() as conn:
        cursor = conn.execute(
            f"DELETE FROM {TABLE_NAME} WHERE id = ?",
            (record_id,)
        )
        # cursor.rowcount gives number of rows deleted
        return cursor.rowcount > 0

def get_record_by_id(record_id: int):
    with get_connection() as conn:
        row = conn.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (record_id,)
        ).fetchone()
        if row:
            columns = ["id", "city", "date_from", "date_to", "data"]
            return dict(zip(columns, row))
        return None
    
def update_record_to_today(record_id: int, date_str: str, data_json: str) -> bool:
    """Set date_from=date_to=today and replace data with the new summary JSON."""
    with get_connection() as conn:
        cur = conn.execute(
            f"""
            UPDATE {TABLE_NAME}
               SET date_from = ?,
                   date_to   = ?,
                   data      = ?
             WHERE id = ?
            """,
            (date_str, date_str, data_json, record_id)
        )
        return cur.rowcount > 0
