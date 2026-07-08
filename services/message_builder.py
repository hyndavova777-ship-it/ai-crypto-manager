from datetime import datetime

def build_alert(
    symbol,
    rank,
    market_cap,
    price,
    volume,
    volume_spike,
    price_change,
    exchange_count,
    exchanges,
    score,
    strength,
    funding_rate,
    open_interest,
    ):
    current_time = datetime.now().strftime("%H:%M:%S")

    text = (
        f"🔥 <b>COINGECKO TRENDING ALERT</b>\n\n"
        f"🪙 <b>Coin:</b> {symbol}\n"
        f"📊 <b>Trending Rank:</b> #{rank}\n"
        f"💎 <b>Market Cap:</b> {market_cap}\n"
        f"💰 <b>Price:</b> ${price:,.6f}\n"
        f"💸 <b>Volume:</b> {volume}\n"
        f"📊 <b>Volume Spike:</b> {volume_spike:.1f}%\n"
        f"📈 <b>24h Change:</b> {price_change:.2f}%\n"
        f"💹 <b>Funding Rate:</b> {funding_rate if funding_rate is not None else 'N/A'}\n"
        f"📊 <b>Open Interest:</b> {open_interest if open_interest is not None else 'N/A'}\n"
        f"🏦 <b>Listed On:</b> {exchange_count} exchanges\n"
        f"📈 <b>Top Exchanges:</b> {exchanges}\n\n"
        f"🤖 <b>AI Score:</b> {score}/10\n"
        f"{strength}\n"
        f"⏰ <b>Time:</b> {current_time}"
    )

    return text