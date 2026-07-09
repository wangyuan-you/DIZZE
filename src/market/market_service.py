from datetime import datetime

from src.database.market_repository import upsert_market_price
from src.market.cache import get_cache_summary
from src.market.steam_client import SteamClient
from src.utils.settings import load_settings


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