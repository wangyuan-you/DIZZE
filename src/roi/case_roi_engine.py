import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT_DIR / "data" / "cases.json"

USD_TWD = 32.0
KEY_PRICE_USD = 2.49

ODDS = {
    "blue": 0.7992,
    "purple": 0.1598,
    "pink": 0.0320,
    "red": 0.0064,
    "gold": 0.0026,
}

DEFAULT_AVG_VALUE_USD = {
    "blue": 0.08,
    "purple": 0.45,
    "pink": 2.5,
    "red": 28.0,
    "gold": 180.0,
}


def load_cases():
    with open(CASES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_ev_usd(case_data):
    avg = case_data.get("avg_value_usd", DEFAULT_AVG_VALUE_USD)

    return (
        avg["blue"] * ODDS["blue"]
        + avg["purple"] * ODDS["purple"]
        + avg["pink"] * ODDS["pink"]
        + avg["red"] * ODDS["red"]
        + avg["gold"] * ODDS["gold"]
    )


def calculate_case_roi(case_data):
    case_price_usd = float(case_data["case_price_usd"])
    total_cost_usd = case_price_usd + KEY_PRICE_USD
    ev_usd = calculate_ev_usd(case_data)
    roi = ev_usd / total_cost_usd if total_cost_usd else 0

    return {
        "name": case_data["name"],
        "case_price_twd": case_price_usd * USD_TWD,
        "key_price_twd": KEY_PRICE_USD * USD_TWD,
        "total_cost_twd": total_cost_usd * USD_TWD,
        "ev_twd": ev_usd * USD_TWD,
        "roi": roi,
        "gold_pool": case_data["gold_pool"],
        "tags": ", ".join(case_data.get("tags", [])),
    }


def get_case_roi_rows():
    cases = load_cases()
    rows = [calculate_case_roi(case) for case in cases]
    rows.sort(key=lambda row: row["roi"], reverse=True)
    return rows