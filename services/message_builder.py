from datetime import datetime

def build_alert(
    symbol,
    price,
    pre_move_score,
    pre_move_breakdown,
    oi_change,
):
    current_time = datetime.now().strftime("%H:%M:%S")

    if oi_change >= 10:
       oi_icon = "🟢"
    elif oi_change >= 5:
         oi_icon = "🟡"
    elif oi_change <= -5:
         oi_icon = "🔴"
    else:
         oi_icon = "⚪"

    text = (
        f"🔥 <b>COINGECKO TRENDING ALERT</b>\n\n"
        f"🪙 <b>Coin:</b> {symbol}\n"
        f"💰 <b>Price:</b> ${price:,.6f}\n"
        f"🚀 <b>Pre-Move Score:</b> {pre_move_score}/10\n"
        f"   ├ Price: {pre_move_breakdown['price_score']}/3\n"
        f"   ├ Volume: {pre_move_breakdown['volume_score']}/3\n"
        f"   ├ OI: {pre_move_breakdown['oi_score']}/2\n"
        f"   ├ Distance: {pre_move_breakdown['distance_score']}/2\n"
        f"   ├ Confluence: {pre_move_breakdown['confluence_score']}/2\n"
        f"   └ Bearish Penalty: -{pre_move_breakdown['bearish_penalty']}\n"
        f"{oi_icon} <b>OI Change:</b> {oi_change:.1f}%\n"
        f"⏰ <b>Time:</b> {current_time}"
    )

    return text