from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from src.database.db import get_connection


def begin_sync_run(
    source_name: str,
    started_at: str,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO catalog_sync_runs (
                source_name,
                status,
                started_at
            )
            VALUES (?, 'running', ?)
            """,
            (source_name, started_at),
        )

        connection.commit()
        return int(cursor.lastrowid)

    finally:
        connection.close()


def finish_sync_run(
    sync_run_id: int,
    status: str,
    finished_at: str,
    cases_count: int,
    items_count: int,
    error_message: str | None = None,
) -> None:
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE catalog_sync_runs
            SET
                status = ?,
                finished_at = ?,
                cases_count = ?,
                items_count = ?,
                error_message = ?
            WHERE id = ?
            """,
            (
                status,
                finished_at,
                cases_count,
                items_count,
                error_message,
                sync_run_id,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def replace_catalog(
    cases: Iterable[dict[str, Any]],
    items: Iterable[dict[str, Any]],
) -> tuple[int, int]:
    case_rows = list(cases)
    item_rows = list(items)

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("BEGIN")

        cursor.execute("DELETE FROM case_catalog_items")
        cursor.execute("DELETE FROM case_catalog")

        cursor.executemany(
            """
            INSERT INTO case_catalog (
                case_id,
                name,
                case_type,
                market_hash_name,
                first_sale_date,
                image_url,
                rare_pool_name,
                source_name,
                source_updated_at
            )
            VALUES (
                :case_id,
                :name,
                :case_type,
                :market_hash_name,
                :first_sale_date,
                :image_url,
                :rare_pool_name,
                :source_name,
                :source_updated_at
            )
            """,
            case_rows,
        )

        cursor.executemany(
            """
            INSERT INTO case_catalog_items (
                case_id,
                source_item_id,
                base_skin_id,
                display_name,
                market_hash_name,
                rarity_id,
                rarity_name,
                rarity_color,
                wear_name,
                stattrak,
                souvenir,
                is_rare,
                image_url,
                source_updated_at
            )
            VALUES (
                :case_id,
                :source_item_id,
                :base_skin_id,
                :display_name,
                :market_hash_name,
                :rarity_id,
                :rarity_name,
                :rarity_color,
                :wear_name,
                :stattrak,
                :souvenir,
                :is_rare,
                :image_url,
                :source_updated_at
            )
            """,
            item_rows,
        )

        connection.commit()
        return len(case_rows), len(item_rows)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def count_catalog_cases() -> int:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM case_catalog
            """
        ).fetchone()

        return int(row["count"]) if row else 0

    finally:
        connection.close()


def count_catalog_items() -> int:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM case_catalog_items
            """
        ).fetchone()

        return int(row["count"]) if row else 0

    finally:
        connection.close()


def count_case_catalog_items(case_id: str) -> int:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM case_catalog_items
            WHERE case_id = ?
            """,
            (case_id,),
        ).fetchone()

        return int(row["count"]) if row else 0

    finally:
        connection.close()


def get_catalog_cases() -> list[dict[str, Any]]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                catalog.case_id,
                catalog.name,
                catalog.case_type,
                catalog.market_hash_name,
                catalog.first_sale_date,
                catalog.image_url,
                catalog.rare_pool_name,
                catalog.source_name,
                catalog.source_updated_at,
                COUNT(items.id) AS item_count
            FROM case_catalog AS catalog
            LEFT JOIN case_catalog_items AS items
                ON items.case_id = catalog.case_id
            GROUP BY catalog.case_id
            ORDER BY catalog.name COLLATE NOCASE
            """
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_catalog_case(
    case_id: str,
) -> dict[str, Any] | None:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                catalog.case_id,
                catalog.name,
                catalog.case_type,
                catalog.market_hash_name,
                catalog.first_sale_date,
                catalog.image_url,
                catalog.rare_pool_name,
                catalog.source_name,
                catalog.source_updated_at,
                COUNT(items.id) AS item_count
            FROM case_catalog AS catalog
            LEFT JOIN case_catalog_items AS items
                ON items.case_id = catalog.case_id
            WHERE catalog.case_id = ?
            GROUP BY catalog.case_id
            """,
            (case_id,),
        ).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


def get_catalog_items(
    case_id: str | None = None,
) -> list[dict[str, Any]]:
    connection = get_connection()

    try:
        if case_id:
            rows = connection.execute(
                """
                SELECT
                    id,
                    case_id,
                    source_item_id,
                    base_skin_id,
                    display_name,
                    market_hash_name,
                    rarity_id,
                    rarity_name,
                    rarity_color,
                    wear_name,
                    stattrak,
                    souvenir,
                    is_rare,
                    image_url,
                    source_updated_at
                FROM case_catalog_items
                WHERE case_id = ?
                ORDER BY
                    is_rare ASC,
                    rarity_name COLLATE NOCASE,
                    display_name COLLATE NOCASE,
                    wear_name COLLATE NOCASE
                """,
                (case_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    id,
                    case_id,
                    source_item_id,
                    base_skin_id,
                    display_name,
                    market_hash_name,
                    rarity_id,
                    rarity_name,
                    rarity_color,
                    wear_name,
                    stattrak,
                    souvenir,
                    is_rare,
                    image_url,
                    source_updated_at
                FROM case_catalog_items
                ORDER BY
                    case_id,
                    is_rare ASC,
                    rarity_name COLLATE NOCASE,
                    display_name COLLATE NOCASE
                """
            ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_catalog_item_by_market_hash(
    market_hash_name: str,
) -> dict[str, Any] | None:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                case_id,
                source_item_id,
                base_skin_id,
                display_name,
                market_hash_name,
                rarity_id,
                rarity_name,
                rarity_color,
                wear_name,
                stattrak,
                souvenir,
                is_rare,
                image_url,
                source_updated_at
            FROM case_catalog_items
            WHERE market_hash_name = ?
            LIMIT 1
            """,
            (market_hash_name,),
        ).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


def get_catalog_rarities(
    case_id: str,
) -> list[str]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT DISTINCT rarity_name
            FROM case_catalog_items
            WHERE
                case_id = ?
                AND rarity_name IS NOT NULL
                AND rarity_name != ''
            ORDER BY rarity_name COLLATE NOCASE
            """,
            (case_id,),
        ).fetchall()

        return [
            str(row["rarity_name"])
            for row in rows
            if row["rarity_name"]
        ]

    finally:
        connection.close()