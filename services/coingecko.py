import requests


def get_trending_data():
    """
    Отримує трендові монети та їх ринкові дані лише за два запити.
    """

    try:
        trending_url = "https://api.coingecko.com/api/v3/search/trending"

        response = requests.get(trending_url, timeout=10)

        if response.status_code != 200:
            print(f"Trending request failed: {response.status_code}")
            return {}

        data = response.json()

        ids = []
        symbols = {}

        for coin in data["coins"]:
            item = coin["item"]

            coin_id = item["id"]

            ids.append(coin_id)

            symbols[coin_id] = item["symbol"].upper()

        if not ids:
            return {}

        markets_url = "https://api.coingecko.com/api/v3/coins/markets"

        params = {
            "vs_currency": "usd",
            "ids": ",".join(ids),
            "order": "market_cap_desc",
            "per_page": len(ids),
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h",
        }

        response = requests.get(
            markets_url,
            params=params,
            timeout=15,
        )

        if response.status_code != 200:
            print(f"Markets request failed: {response.status_code}")
            return {}

        markets = response.json()

        trending = {}

        for coin in markets:

            coin_id = coin["id"]

            symbol = symbols.get(coin_id)

            if not symbol:
                continue

            trending[symbol] = {
                "id": coin_id,
                "rank": coin.get("market_cap_rank", 9999),
                "market_cap": coin.get("market_cap", 0),
                "price": coin.get("current_price", 0),
                "volume": coin.get("total_volume", 0),
                "price_change": coin.get("price_change_percentage_24h", 0) or 0,

                # Поки що ці поля залишаємо порожніми.
                # Пізніше заповнимо їх окремим сервісом.
                "exchange_count": 0,
                "top_exchanges": [],
            }

        return trending

    except Exception as e:
        print("CoinGecko error:", e)
        return {}

def get_coin_info(coin_id):
    """
    Повертає детальну інформацію про монету.
    """

    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

        params = {
            "localization": "false",
            "tickers": "true",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false",
        }

        response = requests.get(url, params=params, timeout=15)

        if response.status_code != 200:
            print(f"CoinGecko status {response.status_code} for {coin_id}")
            return None
            

        data = response.json()

        market = data.get("market_data", {})

        tickers = data.get("tickers", [])

        exchanges = []

        for ticker in tickers:
            market_name = ticker.get("market", {}).get("name")

            if market_name and market_name not in exchanges:
                exchanges.append(market_name)

        return {
            "rank": data.get("market_cap_rank") or 9999,
            "market_cap": market.get("market_cap", {}).get("usd", 0),
            "price": market.get("current_price", {}).get("usd", 0),
            "volume": market.get("total_volume", {}).get("usd", 0),
            "exchange_count": len(exchanges),
            "top_exchanges": exchanges[:10],
        }

    except Exception as e:
        print("CoinGecko coin info error:", e)
        return None