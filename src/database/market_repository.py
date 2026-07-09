from src.database.db import get_connection


def upsert_market_price(item_name, market, price_usd, price_twd, currency, updated_at):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO market_prices (
            item_name,
            market,
            price_usd,
            price_twd,
            currency,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(item_name, market) DO UPDATE SET
            price_usd = excluded.price_usd,
            price_twd = excluded.price_twd,
            currency = excluded.currency,
            updated_at = excluded.updated_at
        """
        ,
        (item_name, market, price_usd, price_twd, currency, updated_at),
    )

    conn.commit()
    conn.close()


def get_market_prices():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT item_name, market, price_usd, price_twd, currency, updated_at
        FROM market_prices
        ORDER BY updated_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "item_name": row[0],
            "market": row[1],
            "price_usd": row[2],
            "price_twd": row[3],
            "currency": row[4],
            "updated_at": row[5],
        }
        for row in rows
    ]


def count_market_prices():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM market_prices")
    count = cursor.fetchone()[0]

    conn.close()
    return count