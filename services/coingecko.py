import requests


def get_trending_data():
    """
    Повертає список трендових монет з CoinGecko.
    """

    try:
        url = "https://api.coingecko.com/api/v3/search/trending"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {}

        data = response.json()

        trending = {}

        for coin in data["coins"]:
            item = coin["item"]

            symbol = item["symbol"].upper()

            coin_data = item.get("data", {})

            trending[symbol] = {
                "id": item["id"],
                "rank": item.get("market_cap_rank"),
                "price": coin_data.get("price"),
                "volume": coin_data.get("total_volume"),
                "price_change": (
                    coin_data.get("price_change_percentage_24h", {})
                    .get("usd", 0)
                ),
            }

        return trending

    except Exception as e:
        print("CoinGecko trending error:", e)
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