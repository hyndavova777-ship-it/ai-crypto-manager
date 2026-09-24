import time 

def calculate_pre_move_score(
    price_5m,
    price_15m,
    price_1h,
    volume_acceleration,
    oi_change,
    distance_to_high,
):
    # -------------------------
    # Component scores
    # -------------------------

    price_score = 0
    volume_score = 0
    oi_score = 0
    distance_score = 0
    confluence_score = 0

    # -------------------------
    # Price Momentum / Early Move (0-3)
    # -------------------------

    if price_5m >= 0.3:
        price_score += 1

    if price_15m >= 1:
        price_score += 1

    if price_1h >= 2:
        price_score += 1

    # -------------------------
    # Overextension Protection
    # -------------------------

    if price_15m > 5:
        price_score -= 1

    if price_1h > 8:
        price_score -= 1

    price_score = max(0, min(price_score, 3))

    # -------------------------
    # Volume Acceleration + Price Confirmation (0-3)
    # -------------------------

    if volume_acceleration >= 200:

        # Strong volume + short-term positive price
        if price_5m > 0:
            volume_score += 3

        # Strong volume but 5m is not positive:
        # require positive 15m and positive 1h
        elif price_15m > 0 and price_1h > 0:
            volume_score += 2

    elif volume_acceleration >= 100:

        if price_5m > 0:
            volume_score += 2

        elif price_15m > 0 and price_1h > 0:
            volume_score += 1

    elif volume_acceleration >= 50:

        if price_5m > 0:
            volume_score += 1

    # -------------------------
    # OI Change + Price Confirmation (0-2)
    # -------------------------

    if oi_change >= 10:

        if price_5m > 0 or price_15m > 0:
            oi_score += 2

    elif oi_change >= 5:

        if price_5m > 0 or price_15m > 0:
            oi_score += 1

    # -------------------------
    # Distance to Local High (0-2)
    # -------------------------

    if distance_to_high <= 2:
        distance_score += 2

    elif distance_to_high <= 5:
        distance_score += 1

    # -------------------------
    # Too Close to Local High
    # -------------------------

    if distance_to_high < 0.5:
        distance_score -= 1

    distance_score = max(0, min(distance_score, 2))

    # -------------------------
    # Confluence Bonus (0-2)
    # Price + Volume + OI
    # -------------------------

    if (
        price_5m > 0
        and volume_acceleration >= 100
        and oi_change >= 5
    ):
        confluence_score += 2

    elif (
        price_15m > 0
        and volume_acceleration >= 100
        and oi_change >= 5
    ):
        confluence_score += 1

    # -------------------------
    # Bearish protection
    # -------------------------

    bearish_penalty = 0

    if price_5m < 0 and price_1h <= -2:
        bearish_penalty = 3

    # -------------------------
    # Final Score
    # -------------------------

    score = (
        price_score
        + volume_score
        + oi_score
        + distance_score
        + confluence_score
        - bearish_penalty
    )

    # -------------------------
    # Breakdown
    # -------------------------

    print(
        f"Pre-Move Breakdown | "
        f"Price: {price_score}/3 | "
        f"Volume: {volume_score}/3 | "
        f"OI: {oi_score}/2 | "
        f"Distance: {distance_score}/2 | "
        f"Confluence: {confluence_score}/2 | "
        f"Bearish Penalty: -{bearish_penalty}"
    )

    return {
    "score": max(0, min(score, 10)),
    "price_score": price_score,
    "volume_score": volume_score,
    "oi_score": oi_score,
    "distance_score": distance_score,
    "confluence_score": confluence_score,
    "bearish_penalty": bearish_penalty,
}