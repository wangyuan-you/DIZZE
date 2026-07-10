from __future__ import annotations

from opencc import OpenCC

from src.utils.settings import load_settings


class TraditionalChineseConverter:
    """將簡體中文轉換成台灣繁體用語。"""

    def __init__(self) -> None:
        settings = load_settings()
        catalog_settings = settings.get("catalog_source", {})

        self.enabled = bool(
            catalog_settings.get(
                "convert_to_traditional",
                True,
            )
        )

        config_name = str(
            catalog_settings.get(
                "opencc_config",
                "s2twp",
            )
        )

        self.converter = OpenCC(config_name)

    def convert(self, value: object) -> str | None:
        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return text

        if not self.enabled:
            return text

        return self.converter.convert(text)