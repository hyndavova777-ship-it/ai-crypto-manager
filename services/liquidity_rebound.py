from datetime import datetime, timezone

REBOUND_TARGET_PCT = 3.0 
REBOUND_WINDOW_SECONDS = 60 * 60

def calculate_cluster_midpoint(cluster_start, cluster_end): 
    """ 
    cluster_start — верхня межа нижнього кластера. 
    cluster_end — нижня межа кластера. 
    """ 
    upper = float(cluster_start) 
    lower = float(cluster_end)

    if upper <= 0 or lower <= 0 or upper <= lower:
        raise ValueError("Invalid cluster boundaries")

    return (upper + lower) / 2

def create_cluster_tracker( 
    symbol, 
    cluster_start, 
    cluster_end, 
    cluster_size_usdt=None, 
    observed_at=None, 
): 
    """ 
    Створює запис для спостереження за кластером.

    Межі кластера повинні бути визначені
    до початку відстеження.
    """
    upper = float(cluster_start)
    lower = float(cluster_end)
    midpoint = calculate_cluster_midpoint(upper, lower)

    if observed_at is None:
        observed_at = datetime.now(timezone.utc).timestamp()

    return {
        "symbol": symbol.upper(),
        "cluster_start": upper,
        "cluster_end": lower,
        "cluster_midpoint": midpoint,
        "cluster_size_usdt": cluster_size_usdt,
        "observed_at": observed_at,
        "status": "WAITING",
        "price_above_midpoint_seen": False,
        "contact_time": None,
        "contact_price": None,
        "lowest_price_after_contact": None,
        "rebound_pct": 0.0,
        "rebound_3pct_hit": False,
        "time_to_rebound_seconds": None,
        "last_update_time": None,
    }

def update_cluster_tracker(tracker, price, timestamp): 
    """
    Оновлює стан за новою ціною.

    Використовує лише поточні та минулі дані.
    """
    price = float(price)
    timestamp = float(timestamp)

    if price <= 0:
        raise ValueError("Price must be positive")

    if timestamp < tracker["observed_at"]:
        return tracker

    last_update = tracker.get("last_update_time")
    if last_update is not None and timestamp <= last_update:
        return tracker

    if tracker["status"] in ("TARGET_HIT", "EXPIRED"):
        return tracker

    tracker["last_update_time"] = timestamp

    if tracker["status"] == "WAITING":
        # Спочатку потрібно побачити ціну вище середини
        if price > tracker["cluster_midpoint"]:
            tracker["price_above_midpoint_seen"] = True
        # Контакт зараховуємо лише після руху зверху вниз
        elif tracker["price_above_midpoint_seen"]:
            tracker["status"] = "MIDPOINT_REACHED"
            tracker["contact_time"] = timestamp
            tracker["contact_price"] = price
            tracker["lowest_price_after_contact"] = price

        return tracker

    if tracker["status"] == "MIDPOINT_REACHED":
        elapsed = timestamp - tracker["contact_time"]

        if elapsed > REBOUND_WINDOW_SECONDS:
            tracker["status"] = "EXPIRED"
            return tracker

        previous_low = tracker["lowest_price_after_contact"]

        # Перевіряємо відновлення від мінімуму,
        # який був відомий ДО поточного спостереження.
        rebound_pct = (
            (price - previous_low) / previous_low
        ) * 100

        tracker["rebound_pct"] = max(
            tracker["rebound_pct"],
            rebound_pct,
        )

        if rebound_pct >= REBOUND_TARGET_PCT:
            tracker["status"] = "TARGET_HIT"
            tracker["rebound_3pct_hit"] = True
            tracker["time_to_rebound_seconds"] = elapsed
            return tracker

        if price < previous_low:
            tracker["lowest_price_after_contact"] = price

    return tracker


def expire_cluster_if_needed(tracker, timestamp):
    """
    Завершує спостереження через 60 хвилин
    після контакту із серединою кластера.
    """
    if tracker["status"] != "MIDPOINT_REACHED":
        return tracker

    contact_time = tracker.get("contact_time")

    if contact_time is None:
        return tracker

    if float(timestamp) > contact_time + REBOUND_WINDOW_SECONDS:
        tracker["status"] = "EXPIRED"
        tracker["last_update_time"] = float(timestamp)

    return tracker
