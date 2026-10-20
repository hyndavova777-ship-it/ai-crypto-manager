from services.liquidity_rebound import ( 
    create_cluster_tracker, 
    update_cluster_tracker, 
)

tracker = create_cluster_tracker( 
    symbol="TEST", 
    cluster_start=2.42, 
    cluster_end=2.38, 
    cluster_size_usdt=8_500_000, 
    observed_at=1000, 
)

print("\n--- LIQUIDATION CLUSTER ---") 
print(f"Cluster Start Price: ${tracker['cluster_start']:.4f}") 
print(f"Cluster Mid Price:   ${tracker['cluster_midpoint']:.4f}") 
print(f"Cluster End Price:   ${tracker['cluster_end']:.4f}") 
print(f"Cluster Size:        ${tracker['cluster_size_usdt']:,.0f}")

print("\n--- COIN PRICE MOVEMENT ---")

prices = [
    (1010, 2.39),
    (1020, 2.38),
    (1030, 2.41),
    (1040, 2.40),
    (1050, 2.39),
    (1060, 2.47),
]

for timestamp, price in prices: 
    tracker = update_cluster_tracker( 
        tracker, price, timestamp 
    )

    print(
        f"Coin Price: ${price:.4f} | "
        f"Status: {tracker['status']} | "
        f"Rebound: {tracker['rebound_pct']:.2f}%"
    )

print("\n--- FINAL RESULT ---")
print("Target Hit:", tracker["rebound_3pct_hit"])
print("Time to Rebound:", tracker["time_to_rebound_seconds"], "sec")