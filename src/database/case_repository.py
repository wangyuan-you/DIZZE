import json
from pathlib import Path

from src.database.db import get_connection
from src.utils.settings import load_settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_JSON_PATH = PROJECT_ROOT / "data" / "cases.json"


def import_cases_from_json():
    settings = load_settings()
    key_price_usd = float(settings["steam_key_price_usd"])

    with open(CASES_JSON_PATH, "r", encoding="utf-8") as file:
        cases = json.load(file)

    conn = get_connection()
    cursor = conn.cursor()

    for case in cases:
        cursor.execute(
            """
            INSERT INTO cases (
                name,
                case_price_usd,
                key_price_usd,
                gold_pool,
                tags,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(name) DO UPDATE SET
                case_price_usd = excluded.case_price_usd,
                key_price_usd = excluded.key_price_usd,
                gold_pool = excluded.gold_pool,
                tags = excluded.tags,
                updated_at = datetime('now')
            """,
            (
                case["name"],
                float(case["case_price_usd"]),
                key_price_usd,
                case["gold_pool"],
                ", ".join(case.get("tags", [])),
            ),
        )

    conn.commit()
    conn.close()


def get_cases_from_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            name,
            case_price_usd,
            key_price_usd,
            gold_pool,
            tags,
            updated_at
        FROM cases
        ORDER BY name ASC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "name": row[0],
            "case_price_usd": row[1],
            "key_price_usd": row[2],
            "gold_pool": row[3],
            "tags": row[4],
            "updated_at": row[5],
        }
        for row in rows
    ]