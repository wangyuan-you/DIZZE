from __future__ import annotations

from typing import Any

import requests

from src.utils.settings import load_settings


class CsgoApiClient:
    def __init__(self) -> None:
        settings = load_settings()
        source_settings = settings["catalog_source"]

        self.source_name = str(source_settings["name"])
        self.language = str(source_settings.get("language", "en"))
        self.base_url = str(source_settings["base_url"]).rstrip("/")
        self.timeout_seconds = int(
            source_settings.get("timeout_seconds", 30)
        )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "DIZZE-CS2-Skin-Terminal/"
                    f"{settings.get('version', '0.9.0')}"
                ),
                "Accept": "application/json",
            }
        )

    def _get_json(self, filename: str) -> Any:
        url = f"{self.base_url}/{self.language}/{filename}"

        response = self.session.get(
            url,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        return response.json()

    def fetch_crates(self) -> list[dict[str, Any]]:
        payload = self._get_json("crates.json")

        if not isinstance(payload, list):
            raise ValueError("crates.json response is not a list")

        return payload

    def fetch_skin_variants(self) -> list[dict[str, Any]]:
        payload = self._get_json("skins_not_grouped.json")

        if not isinstance(payload, list):
            raise ValueError(
                "skins_not_grouped.json response is not a list"
            )

        return payload