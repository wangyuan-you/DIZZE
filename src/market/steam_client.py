import requests


class SteamClient:
    def __init__(self):
        self.market_name = "Steam"
        self.base_url = "https://steamcommunity.com/market/priceoverview/"

    def get_status(self):
        return {
            "market": self.market_name,
            "status": "Ready",
            "message": "Steam priceoverview endpoint ready",
        }

    def fetch_price(self, item_name, appid=730, currency=1):
        params = {
            "appid": appid,
            "currency": currency,
            "market_hash_name": item_name,
        }

        response = requests.get(
            self.base_url,
            params=params,
            timeout=15
        )

        if response.status_code == 429:
            raise Exception("Steam Rate Limit")

        response.raise_for_status()

        if response.status_code != 200:
            print(response.status_code)
            return None

        data = response.json()

        if not data.get("success"):
            return None

        price_text = data.get("lowest_price") or data.get("median_price")

        if not price_text:
            return None

        return {
            "item_name": item_name,
            "market": self.market_name,
            "raw_price": price_text,
        }
    