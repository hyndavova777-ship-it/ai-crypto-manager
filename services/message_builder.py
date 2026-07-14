from datetime import datetime

def build_alert(
    symbol,
    rank,
    market_cap,
    price,
    volume,
    volume_ratio,
    price_change,
    exchange_count,
    exchanges,
    score,
    strength,
    funding_rate,
    open_interest,
    ):
    current_time = datetime.now().strftime("%H:%M:%S")

    if funding_rate >= 0:
        funding_icon = "🟢"
    else:
        funding_icon = "🔴"

    if open_interest is None:
        oi_text = "N/A"
    elif open_interest >= 1_000_000_000:
        oi_text = f"{open_interest / 1_000_000_000:.2f}B"
    elif open_interest >= 1_000_000:
        oi_text = f"{open_interest / 1_000_000:.2f}M"
    elif open_interest >= 1_000:
        oi_text = f"{open_interest / 1_000:.2f}K"
    else:
        oi_text = f"{open_interest:.2f}"

    text = (
        f"🔥 <b>COINGECKO TRENDING ALERT</b>\n\n"
        f"🪙 <b>Coin:</b> {symbol}\n"
        f"📊 <b>Trending Rank:</b> #{rank}\n"
        f"💎 <b>Market Cap:</b> {market_cap}\n"
        f"💰 <b>Price:</b> ${price:,.6f}\n"
        f"💸 <b>Volume:</b> {volume}\n"
        f"📊 <b>Volume Ratio:</b> {volume_ratio:.2%}\n"
        f"📈 <b>24h Change:</b> {price_change:.2f}%\n"
        f"{funding_icon} <b>Funding Rate:</b> {funding_rate * 100:.4f}%\n"
        f"📊 <b>Open Interest:</b> {oi_text}\n"
        f"🏦 <b>Binance Futures:</b> {'✅' if open_interest else '❌'}\n"
        f"🤖 <b>AI Score:</b> {score}/10\n"
        f"{strength}\n"
        f"⏰ <b>Time:</b> {current_time}"
    )

    return text