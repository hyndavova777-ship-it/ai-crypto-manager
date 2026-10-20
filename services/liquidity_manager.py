
from services.liquidity_rebound import (
    update_cluster_tracker,
    expire_cluster_if_needed,
)
from services.liquidity_storage import (
    load_liquidity_clusters,
    save_liquidity_clusters,
)


def update_liquidity_clusters(prices, timestamp):
    clusters = load_liquidity_clusters()

    updated = 0
    target_hits = 0
    expired = 0

    for cluster_id, tracker in clusters.items():
        if tracker["status"] in ("TARGET_HIT", "EXPIRED"):
            continue

        previous_status = tracker["status"]

        tracker = expire_cluster_if_needed(tracker, timestamp)

        if tracker["status"] == "EXPIRED":
            expired += 1
            updated += 1
            clusters[cluster_id] = tracker
            continue

        symbol = tracker["symbol"]

        if symbol not in prices:
            continue

        tracker = update_cluster_tracker(
            tracker,
            prices[symbol],
            timestamp,
        )

        clusters[cluster_id] = tracker
        updated += 1

        if (
            previous_status != "TARGET_HIT"
            and tracker["status"] == "TARGET_HIT"
        ):
            target_hits += 1

    if updated:
        save_liquidity_clusters(clusters)

    return {
        "updated": updated,
        "target_hits": target_hits,
        "expired": expired,
        "total_clusters": len(clusters),
    }

