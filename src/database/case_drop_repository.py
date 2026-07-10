from __future__ import annotations

from src.database.db import get_connection


def upsert_case_drop(
    case_name: str,
    item_name: str,
    rarity: str,
    probability: float,
    market_price_usd: float = 0.0,
    updated_at: str | None = None,
) -> None:
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO case_drops (
                case_name,
                item_name,
                rarity,
                probability,
                market_price_usd,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(case_name, item_name) DO UPDATE SET
                rarity = excluded.rarity,
                probability = excluded.probability,
                market_price_usd = excluded.market_price_usd,
                updated_at = excluded.updated_at
            """,
            (
                case_name,
                item_name,
                rarity,
                probability,
                market_price_usd,
                updated_at,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def get_case_drops(case_name: str) -> list[dict]:
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                item_name,
                rarity,
                probability,
                market_price_usd,
                updated_at
            FROM case_drops
            WHERE case_name = ?
            ORDER BY rarity, item_name
            """,
            (case_name,),
        )

        rows = cursor.fetchall()

        return [
            {
                "item_name": row[0],
                "rarity": row[1],
                "probability": row[2],
                "market_price_usd": row[3],
                "updated_at": row[4],
            }
            for row in rows
        ]

    finally:
        connection.close()


def count_case_drops(case_name: str | None = None) -> int:
    connection = get_connection()

    try:
        cursor = connection.cursor()

        if case_name is None:
            cursor.execute("SELECT COUNT(*) FROM case_drops")
        else:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM case_drops
                WHERE case_name = ?
                """,
                (case_name,),
            )

        result = cursor.fetchone()
        return int(result[0]) if result else 0

    finally:
        connection.close()