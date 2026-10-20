
MIN_LEVEL_LIQUIDITY_USDT = 500_000


def detect_btc_clusters(levels, current_price):
    """
    Визначає LONG-кластери BTC нижче поточної ціни.

    levels — послідовні цінові рівні Heatmap:
    [
        {"price": 79700, "size_usdt": 530000},
        {"price": 79600, "size_usdt": 650000},
    ]

    Кожен рівень повинен містити ОКРЕМИЙ
    обсяг ліквідацій, не накопичену суму.

    Вхідні рівні мають утворювати повну
    послідовність цінових інтервалів.
    """

    current_price = float(current_price)

    if current_price <= 0:
        raise ValueError("Invalid BTC price")

    if not levels:
        return []

    normalized = []

    for level in levels:
        price = float(level["price"])
        size = float(level["size_usdt"])

        if price <= 0 or size < 0:
            raise ValueError("Invalid liquidation level")

        normalized.append({
            "price": price,
            "size_usdt": size,
        })

    # Впорядковуємо рівні за спаданням ціни.
    normalized.sort(
        key=lambda item: item["price"],
        reverse=True,
    )

    # Не допускаємо повторення цінових рівнів.
    prices = [item["price"] for item in normalized]

    if len(prices) != len(set(prices)):
        raise ValueError("Duplicate price levels")

    clusters = []
    active_group = []

    def finalize_group(group):
        if len(group) < 2:
            return

        upper = group[0]["price"]
        lower = group[-1]["price"]

        total_size = sum(
            item["size_usdt"] for item in group
        )

        clusters.append({
            "symbol": "BTC",
            "cluster_start": upper,
            "cluster_end": lower,
            "cluster_midpoint": (upper + lower) / 2,
            "cluster_size_usdt": total_size,
            "min_level_size_usdt": min(
                item["size_usdt"] for item in group
            ),
            "level_count": len(group),
            "distance_pct": (
                (current_price - (upper + lower) / 2)
                / current_price * 100
            ),
        })

    for level in normalized:
        eligible = (
            level["price"] < current_price
            and level["size_usdt"]
            >= MIN_LEVEL_LIQUIDITY_USDT
        )

        if eligible:
            active_group.append(level)
        else:
            finalize_group(active_group)
            active_group = []

    finalize_group(active_group)

    clusters.sort(
        key=lambda cluster: cluster["cluster_size_usdt"],
        reverse=True,
    )

    return clusters

