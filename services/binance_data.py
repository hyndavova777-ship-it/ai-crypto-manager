import requests


def get_open_interest(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}USDT"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        return float(data["openInterest"])

    except:
        return None
    
def get_funding_rate(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}USDT"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        return float(data["lastFundingRate"])

    except:
        return None