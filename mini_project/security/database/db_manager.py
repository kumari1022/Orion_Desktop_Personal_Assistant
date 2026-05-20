import sqlite3
import os

DB_PATH = "security/database/users.db"

def init_db():
    os.makedirs("security/database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS face_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image BLOB,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS voice_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            features BLOB,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()