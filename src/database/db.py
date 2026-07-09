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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            source TEXT NOT NULL,
            price_usd REAL NOT NULL,
            price_twd REAL NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            source TEXT NOT NULL,
            price_usd REAL NOT NULL,
            price_twd REAL NOT NULL,
            recorded_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            market TEXT NOT NULL,
            price_usd REAL NOT NULL,
            price_twd REAL NOT NULL,
            currency TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(item_name, market)
        )
    """)

    conn.commit()
    conn.close()