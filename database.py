# database.py
import sqlite3
import os

DB_PATH = os.getenv("DATABASE_PATH", "data/osint.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS osint_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        user TEXT,
        text TEXT,
        sentiment REAL,
        timestamp TEXT,
        url TEXT UNIQUE
    )
    """)
    conn.commit()
    conn.close()

def save_to_db(records):
    if not records:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    for r in records:
        cur.execute("""
        INSERT OR IGNORE INTO osint_data (platform, user, text, sentiment, timestamp, url)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            r.get('platform', ''),
            r.get('user', ''),
            r.get('text', ''),
            float(r.get('sentiment') or 0),
            r.get('timestamp') or '',
            r.get('url') or ''
        ))
    conn.commit()
    conn.close()
    return len(records)
