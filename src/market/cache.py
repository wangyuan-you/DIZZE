from src.database.market_repository import count_market_prices, get_market_prices


def get_cache_summary():
    return {
        "count": count_market_prices(),
        "items": get_market_prices(),
    }