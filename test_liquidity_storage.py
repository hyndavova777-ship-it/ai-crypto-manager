
from services.liquidity_rebound import (
    create_cluster_tracker,
    update_cluster_tracker,
)

from services.liquidity_storage import (
    save_cluster,
    get_cluster,
)


cluster_id = "TEST_USDT_001"

tracker = create_cluster_tracker(
    symbol="TEST",
    cluster_start=2.42,
    cluster_end=2.38,
    cluster_size_usdt=8_500_000,
    observed_at=1000,
)

# Спочатку ціна вище середини кластера
tracker = update_cluster_tracker(tracker, 2.41, 1010)

# Ціна досягає середини
tracker = update_cluster_tracker(tracker, 2.40, 1020)

# Зберігаємо стан
save_cluster(cluster_id, tracker)

print("\n--- CLUSTER SAVED ---")
print("Cluster ID:", cluster_id)
print("Cluster Mid Price:", tracker["cluster_midpoint"])
print("Status:", tracker["status"])

# Завантажуємо стан із JSON
restored = get_cluster(cluster_id)

print("\n--- CLUSTER RESTORED ---")
print("Cluster ID:", cluster_id)
print("Status:", restored["status"])
print("Contact Price:", restored["contact_price"])

# Продовжуємо аналіз після відновлення
restored = update_cluster_tracker(restored, 2.39, 1030)
restored = update_cluster_tracker(restored, 2.47, 1040)

save_cluster(cluster_id, restored)

print("\n--- FINAL RESULT ---")
print("Status:", restored["status"])
print("Rebound:", f"{restored['rebound_pct']:.2f}%")
print("Target Hit:", restored["rebound_3pct_hit"])
print(
    "Time to Rebound:",
    restored["time_to_rebound_seconds"],
    "sec",
)
