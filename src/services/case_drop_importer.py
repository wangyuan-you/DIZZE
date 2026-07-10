from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.database.case_drop_repository import upsert_case_drop


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASE_DROPS_PATH = PROJECT_ROOT / "data" / "case_drops.json"


def import_case_drops_from_json() -> int:
    if not CASE_DROPS_PATH.exists():
        raise FileNotFoundError(
            f"Case drops file not found: {CASE_DROPS_PATH}"
        )

    with CASE_DROPS_PATH.open("r", encoding="utf-8") as file:
        case_groups = json.load(file)

    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    imported_count = 0

    for case_group in case_groups:
        case_name = case_group["case_name"]

        for drop in case_group.get("drops", []):
            upsert_case_drop(
                case_name=case_name,
                item_name=drop["item_name"],
                rarity=drop["rarity"],
                probability=float(drop["probability"]),
                market_price_usd=float(
                    drop.get("market_price_usd", 0)
                ),
                updated_at=updated_at,
            )

            imported_count += 1

    return imported_count