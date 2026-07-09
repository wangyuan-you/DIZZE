from src.database.case_repository import get_cases_from_db
from src.utils.settings import load_settings

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


def calculate_ev_usd():
    return (
        DEFAULT_AVG_VALUE_USD["blue"] * ODDS["blue"]
        + DEFAULT_AVG_VALUE_USD["purple"] * ODDS["purple"]
        + DEFAULT_AVG_VALUE_USD["pink"] * ODDS["pink"]
        + DEFAULT_AVG_VALUE_USD["red"] * ODDS["red"]
        + DEFAULT_AVG_VALUE_USD["gold"] * ODDS["gold"]
    )


def calculate_case_roi(case_data):
    settings = load_settings()
    usd_twd = float(settings["usd_twd"])

    case_price_usd = float(case_data["case_price_usd"])
    key_price_usd = float(case_data["key_price_usd"])
    total_cost_usd = case_price_usd + key_price_usd

    ev_usd = calculate_ev_usd()
    roi = ev_usd / total_cost_usd if total_cost_usd else 0

    return {
        "name": case_data["name"],
        "case_price_twd": case_price_usd * usd_twd,
        "key_price_twd": key_price_usd * usd_twd,
        "total_cost_twd": total_cost_usd * usd_twd,
        "ev_twd": ev_usd * usd_twd,
        "roi": roi,
        "gold_pool": case_data["gold_pool"],
        "tags": case_data["tags"],
        "updated_at": case_data["updated_at"],
    }


def get_case_roi_rows():
    cases = get_cases_from_db()
    rows = [calculate_case_roi(case) for case in cases]
    rows.sort(key=lambda row: row["roi"], reverse=True)
    return rows