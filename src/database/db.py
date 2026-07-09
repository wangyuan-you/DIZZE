import sqlite3
from pathlib import Path

from src.utils.settings import load_settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_db_path():
    settings = load_settings()
    return PROJECT_ROOT / settings["database_path"]


def get_connection():
    db_path = get_db_path()
    db_path.parent.mkdir(exist_ok=True)
    return sqlite3.connect(db_path)


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            case_price_usd REAL NOT NULL,
            key_price_usd REAL NOT NULL,
            gold_pool TEXT NOT NULL,
            tags TEXT,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()