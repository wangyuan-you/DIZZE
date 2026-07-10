from __future__ import annotations

import sqlite3
from pathlib import Path

from src.utils.settings import load_settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_db_path() -> Path:
    settings = load_settings()
    return PROJECT_ROOT / settings["database_path"]


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")

    return connection


def init_database() -> None:
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # 舊版 ROI 引擎仍會使用的箱子價格表。
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                case_price_usd REAL NOT NULL DEFAULT 0,
                key_price_usd REAL NOT NULL DEFAULT 2.49,
                gold_pool TEXT NOT NULL DEFAULT '',
                tags TEXT,
                updated_at TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                source TEXT NOT NULL,
                price_usd REAL NOT NULL,
                price_twd REAL NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS market_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                source TEXT NOT NULL,
                price_usd REAL NOT NULL,
                price_twd REAL NOT NULL,
                recorded_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
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
            """
        )

        # 舊版平均池 EV 測試資料。
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS case_drops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_name TEXT NOT NULL,
                item_name TEXT NOT NULL,
                rarity TEXT NOT NULL,
                probability REAL NOT NULL,
                market_price_usd REAL NOT NULL DEFAULT 0,
                updated_at TEXT,
                UNIQUE(case_name, item_name)
            )
            """
        )

        # v0.9：從社群資料源同步的正式箱子目錄。
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS case_catalog (
                case_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                case_type TEXT NOT NULL,
                market_hash_name TEXT,
                first_sale_date TEXT,
                image_url TEXT,
                rare_pool_name TEXT,
                source_name TEXT NOT NULL,
                source_updated_at TEXT NOT NULL
            )
            """
        )

        # v0.9：箱子內的實際物品與可交易磨損版本。
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS case_catalog_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                source_item_id TEXT,
                base_skin_id TEXT,
                display_name TEXT NOT NULL,
                market_hash_name TEXT,
                rarity_id TEXT,
                rarity_name TEXT,
                rarity_color TEXT,
                wear_name TEXT,
                stattrak INTEGER NOT NULL DEFAULT 0,
                souvenir INTEGER NOT NULL DEFAULT 0,
                is_rare INTEGER NOT NULL DEFAULT 0,
                image_url TEXT,
                source_updated_at TEXT NOT NULL,

                FOREIGN KEY (case_id)
                    REFERENCES case_catalog(case_id)
                    ON DELETE CASCADE,

                UNIQUE (
                    case_id,
                    source_item_id,
                    market_hash_name,
                    stattrak,
                    souvenir,
                    is_rare
                )
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_catalog_items_case_id
            ON case_catalog_items(case_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_catalog_items_market_hash_name
            ON case_catalog_items(market_hash_name)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_catalog_items_rarity
            ON case_catalog_items(rarity_id)
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS catalog_sync_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                cases_count INTEGER NOT NULL DEFAULT 0,
                items_count INTEGER NOT NULL DEFAULT 0,
                error_message TEXT
            )
            """
        )

        connection.commit()

    finally:
        connection.close()