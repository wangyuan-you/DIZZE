import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.json"


def load_settings():
    with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)