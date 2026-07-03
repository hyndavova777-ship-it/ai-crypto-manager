import requests
def get_trending_data():

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

            rank = item.get("market_cap_rank")

            coin_data = item.get("data", {})

            volume = coin_data.get("total_volume")
            price = coin_data.get("price")
            price_change = coin_data.get("price_change_percentage_24h", {}).get("usd")

            trending[symbol] = {
                "id": item["id"],
                "rank": rank,
                "volume": volume,
                "price": price,
                "price_change": price_change
            }

        return trending

    except:
        return {}
    
def get_coin_info(symbol):
    """
    Тимчасова заглушка.
    Пізніше повернемо повну реалізацію.
    """
    return None