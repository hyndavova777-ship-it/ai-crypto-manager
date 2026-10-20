
from services.liquidity_rebound import (
    create_cluster_tracker,
    update_cluster_tracker,
)
from services.liquidity_storage import (
    save_cluster,
    get_cluster,
)
from services.liquidity_manager import update_liquidity_clusters


cluster_id = "TEST_EXPIRATION_001"

tracker = create_cluster_tracker(
    symbol="BTC",
    cluster_start=68000,
    cluster_end=66000,
    observed_at=1000,
)

tracker = update_cluster_tracker(tracker, 69000, 1010)
tracker = update_cluster_tracker(tracker, 67000, 1020)

save_cluster(cluster_id, tracker)

print("\n--- BEFORE EXPIRATION ---")
print("Status:", get_cluster(cluster_id)["status"])

result = update_liquidity_clusters(
    prices={},
    timestamp=1020 + 3601,
)

restored = get_cluster(cluster_id)

print("\n--- AFTER EXPIRATION ---")
print("Status:", restored["status"])
print("Expired:", result["expired"])

assert restored["status"] == "EXPIRED"
assert result["expired"] >= 1

print("\n--- TEST PASSED ---")
