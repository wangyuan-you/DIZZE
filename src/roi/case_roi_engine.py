from __future__ import annotations

from src.database.case_drop_repository import get_case_drops
from src.database.case_repository import get_cases_from_db
from src.utils.settings import load_settings


def calculate_case_ev_usd(case_name: str) -> float:
    drops = get_case_drops(case_name)

    if not drops:
        return 0.0

    expected_value = 0.0

    for drop in drops:
        probability = float(drop.get("probability", 0))
        market_price_usd = float(
            drop.get("market_price_usd", 0)
        )

        expected_value += probability * market_price_usd

    return expected_value


def calculate_case_roi(case_data: dict) -> dict:
    settings = load_settings()

    usd_twd = float(settings["usd_twd"])
    steam_fee_rate = float(
        settings.get("steam_fee_rate", 0.15)
    )

    case_price_usd = float(case_data["case_price_usd"])
    key_price_usd = float(case_data["key_price_usd"])

    total_cost_usd = case_price_usd + key_price_usd

    gross_ev_usd = calculate_case_ev_usd(
        case_data["name"]
    )

    net_ev_usd = gross_ev_usd * (1 - steam_fee_rate)

    expected_profit_usd = net_ev_usd - total_cost_usd

    roi_ratio = (
        expected_profit_usd / total_cost_usd
        if total_cost_usd > 0
        else 0.0
    )

    return {
        "name": case_data["name"],
        "case_price_twd": case_price_usd * usd_twd,
        "key_price_twd": key_price_usd * usd_twd,
        "total_cost_twd": total_cost_usd * usd_twd,
        "gross_ev_twd": gross_ev_usd * usd_twd,
        "ev_twd": net_ev_usd * usd_twd,
        "profit_twd": expected_profit_usd * usd_twd,
        "roi": roi_ratio,
        "gold_pool": case_data["gold_pool"],
        "tags": case_data["tags"],
        "updated_at": case_data["updated_at"],
    }


def get_case_roi_rows() -> list[dict]:
    cases = get_cases_from_db()

    rows = [
        calculate_case_roi(case)
        for case in cases
    ]

    rows.sort(
        key=lambda row: row["roi"],
        reverse=True,
    )

    return rows