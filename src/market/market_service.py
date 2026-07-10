import re
from datetime import datetime
import time
from src.database.market_repository import upsert_market_price
from src.market.cache import get_cache_summary
from src.market.steam_client import SteamClient
from src.utils.settings import load_settings
from src.database.case_repository import update_case_price
from src.database.case_repository import get_cases_from_db


class MarketService:
    def __init__(self):
        self.settings = load_settings()
        self.client = SteamClient()

    def get_market_status(self):
        cache = get_cache_summary()
        steam_status = self.client.get_status()

        return {
            "market": steam_status["market"],
            "status": steam_status["status"],
            "cache_count": cache["count"],
            "currency": self.settings["currency"],
        }

    def parse_price_usd(self, raw_price):
        if not raw_price:
            return None

        cleaned = raw_price.replace(",", "")
        match = re.search(r"[\d.]+", cleaned)

        if not match:
            return None

        return float(match.group())

    def update_single_item_price(self, item_name):
        result = self.client.fetch_price(item_name)

        if not result:
            return None

        price_usd = self.parse_price_usd(result["raw_price"])
        if price_usd is None:
            return None

        usd_twd = float(self.settings["usd_twd"])
        price_twd = price_usd * usd_twd
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        upsert_market_price(
            item_name=item_name,
            market="Steam",
            price_usd=price_usd,
            price_twd=price_twd,
            currency="USD",
            updated_at=now,
        )
        update_case_price(item_name, price_usd)

        return {
            "item_name": item_name,
            "price_usd": price_usd,
            "price_twd": price_twd,
            "updated_at": now,
        }

    def seed_demo_prices(self):
        usd_twd = float(self.settings["usd_twd"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        demo_prices = [
            ("Fracture Case", 0.35),
            ("Dreams & Nightmares Case", 1.20),
            ("Kilowatt Case", 0.85),
            ("Revolution Case", 0.65),
        ]

        for item_name, price_usd in demo_prices:
            upsert_market_price(
                item_name=item_name,
                market="Steam",
                price_usd=price_usd,
                price_twd=price_usd * usd_twd,
                currency="USD",
                updated_at=now,
            )


    def update_all_prices(self):

        print("Loading Cases")

        cases = get_cases_from_db()

        print(len(cases))

        results = []

        for case in cases:

            print(case["name"])

            try:

                result = self.update_single_item_price(case["name"])

                print(result)

                if result:
                    results.append(result)

            except Exception as e:

                print(e)

        time.sleep(1.5)

        print("ALL DONE")

        return results