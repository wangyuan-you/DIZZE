from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from src.database.catalog_repository import (
    begin_sync_run,
    finish_sync_run,
    replace_catalog,
)
from src.services.csgo_api_client import CsgoApiClient
from src.utils.traditional_chinese import (
    TraditionalChineseConverter,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASE_NAME_OVERRIDES_PATH = (
    PROJECT_ROOT
    / "data"
    / "translations"
    / "case_names_zh_tw.json"
)


class CaseCatalogSyncService:
    def __init__(self) -> None:
        self.client = CsgoApiClient()
        self.converter = TraditionalChineseConverter()
        self.case_name_overrides = self._load_case_name_overrides()

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _load_case_name_overrides() -> dict[str, str]:
        if not CASE_NAME_OVERRIDES_PATH.exists():
            return {}

        with CASE_NAME_OVERRIDES_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(file)

        if not isinstance(payload, dict):
            raise ValueError(
                "case_names_zh_tw.json 必須是 JSON object"
            )

        return {
            str(key).strip(): str(value).strip()
            for key, value in payload.items()
            if str(key).strip() and str(value).strip()
        }

    def _get_localized_case_name(
        self,
        original_case_name: str,
        market_hash_name: str | None,
    ) -> str:
        lookup_keys = [
            market_hash_name,
            original_case_name,
        ]

        for key in lookup_keys:
            if key and key in self.case_name_overrides:
                return self.case_name_overrides[key]

        converted = self.converter.convert(original_case_name)

        return converted or original_case_name

    def _display_text(
        self,
        value: object,
        fallback: str | None = None,
    ) -> str | None:
        converted = self.converter.convert(value)

        if converted:
            return converted

        return fallback

    @staticmethod
    def _rarity_fields(
        item: dict[str, Any],
    ) -> tuple[str | None, str | None, str | None]:
        rarity = item.get("rarity") or {}

        return (
            rarity.get("id"),
            rarity.get("name"),
            rarity.get("color"),
        )

    @staticmethod
    def _build_variant_index(
        variants: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        index: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for variant in variants:
            skin_id = variant.get("skin_id")

            if skin_id:
                index[str(skin_id)].append(variant)

        return dict(index)

    def _normalize_regular_item(
        self,
        case_id: str,
        base_item: dict[str, Any],
        variant: dict[str, Any],
        synced_at: str,
    ) -> dict[str, Any]:
        rarity_id, rarity_name, rarity_color = (
            self._rarity_fields(base_item)
        )

        wear = variant.get("wear") or {}

        display_name = (
            variant.get("name")
            or base_item.get("name")
            or "未知物品"
        )

        return {
            "case_id": case_id,
            "source_item_id": variant.get("id"),
            "base_skin_id": base_item.get("id"),
            "display_name": self._display_text(
                display_name,
                "未知物品",
            ),
            "market_hash_name": variant.get(
                "market_hash_name"
            ),
            "rarity_id": rarity_id,
            "rarity_name": self._display_text(
                rarity_name
            ),
            "rarity_color": rarity_color,
            "wear_name": self._display_text(
                wear.get("name")
            ),
            "stattrak": int(
                bool(variant.get("stattrak"))
            ),
            "souvenir": int(
                bool(variant.get("souvenir"))
            ),
            "is_rare": 0,
            "image_url": (
                variant.get("image")
                or base_item.get("image")
            ),
            "source_updated_at": synced_at,
        }

    def _normalize_unexpanded_item(
        self,
        case_id: str,
        item: dict[str, Any],
        synced_at: str,
        is_rare: bool,
    ) -> dict[str, Any]:
        rarity_id, rarity_name, rarity_color = (
            self._rarity_fields(item)
        )

        return {
            "case_id": case_id,
            "source_item_id": item.get("id"),
            "base_skin_id": item.get("id"),
            "display_name": self._display_text(
                item.get("name"),
                "未知物品",
            ),
            "market_hash_name": item.get(
                "market_hash_name"
            ),
            "rarity_id": rarity_id,
            "rarity_name": self._display_text(
                rarity_name
            ),
            "rarity_color": rarity_color,
            "wear_name": None,
            "stattrak": 0,
            "souvenir": 0,
            "is_rare": int(is_rare),
            "image_url": item.get("image"),
            "source_updated_at": synced_at,
        }

    def synchronize(self) -> dict[str, Any]:
        started_at = self._now()

        sync_run_id = begin_sync_run(
            source_name=self.client.source_name,
            started_at=started_at,
        )

        cases_count = 0
        items_count = 0

        try:
            crates = self.client.fetch_crates()
            skin_variants = self.client.fetch_skin_variants()

            variant_index = self._build_variant_index(
                skin_variants
            )

            synced_at = self._now()

            normalized_cases: list[dict[str, Any]] = []
            normalized_items: list[dict[str, Any]] = []

            for crate in crates:
                if crate.get("type") != "Case":
                    continue

                case_id = str(
                    crate.get("id") or ""
                ).strip()

                original_case_name = str(
                    crate.get("name") or ""
                ).strip()

                market_hash_name = crate.get(
                    "market_hash_name"
                )

                if not case_id or not original_case_name:
                    continue

                localized_case_name = (
                    self._get_localized_case_name(
                        original_case_name,
                        str(market_hash_name)
                        if market_hash_name
                        else None,
                    )
                )

                loot_list = crate.get("loot_list") or {}

                normalized_cases.append(
                    {
                        "case_id": case_id,
                        "name": localized_case_name,
                        "case_type": (
                            self._display_text(
                                crate.get("type"),
                                "武器箱",
                            )
                            or "武器箱"
                        ),
                        "market_hash_name": market_hash_name,
                        "first_sale_date": crate.get(
                            "first_sale_date"
                        ),
                        "image_url": crate.get("image"),
                        "rare_pool_name": self._display_text(
                            loot_list.get("name")
                        ),
                        "source_name": self.client.source_name,
                        "source_updated_at": synced_at,
                    }
                )

                for base_item in crate.get("contains") or []:
                    base_skin_id = str(
                        base_item.get("id") or ""
                    )

                    variants = variant_index.get(
                        base_skin_id,
                        [],
                    )

                    if variants:
                        for variant in variants:
                            normalized_items.append(
                                self._normalize_regular_item(
                                    case_id=case_id,
                                    base_item=base_item,
                                    variant=variant,
                                    synced_at=synced_at,
                                )
                            )
                    else:
                        normalized_items.append(
                            self._normalize_unexpanded_item(
                                case_id=case_id,
                                item=base_item,
                                synced_at=synced_at,
                                is_rare=False,
                            )
                        )

                for rare_item in (
                    crate.get("contains_rare") or []
                ):
                    normalized_items.append(
                        self._normalize_unexpanded_item(
                            case_id=case_id,
                            item=rare_item,
                            synced_at=synced_at,
                            is_rare=True,
                        )
                    )

            cases_count, items_count = replace_catalog(
                normalized_cases,
                normalized_items,
            )

            finished_at = self._now()

            finish_sync_run(
                sync_run_id=sync_run_id,
                status="success",
                finished_at=finished_at,
                cases_count=cases_count,
                items_count=items_count,
            )

            return {
                "status": "success",
                "source": self.client.source_name,
                "language": self.client.language,
                "display_language": "zh-TW",
                "case_name_overrides": len(
                    self.case_name_overrides
                ),
                "cases_count": cases_count,
                "items_count": items_count,
                "started_at": started_at,
                "finished_at": finished_at,
            }

        except Exception as error:
            finished_at = self._now()

            finish_sync_run(
                sync_run_id=sync_run_id,
                status="failed",
                finished_at=finished_at,
                cases_count=cases_count,
                items_count=items_count,
                error_message=str(error),
            )

            raise