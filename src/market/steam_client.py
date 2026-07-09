class SteamClient:
    def __init__(self):
        self.market_name = "Steam"

    def get_status(self):
        return {
            "market": self.market_name,
            "status": "Offline",
            "message": "Steam integration will be enabled in v0.8",
        }

    def fetch_price(self, item_name):
        raise NotImplementedError("Real Steam price fetching starts in v0.8")