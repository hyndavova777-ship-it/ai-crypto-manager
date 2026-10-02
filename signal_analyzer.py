import json

import statistics

SIGNAL_HISTORY_FILE = "data/signal_history.json"

def load_completed_signals(): 
    try: 
        with open(SIGNAL_HISTORY_FILE, "r") as f: 
            history = json.load(f)
    except FileNotFoundError:
        print("signal_history.json not found.")
        return []

    except json.JSONDecodeError:
        print("signal_history.json contains invalid JSON.")
        return []

    completed_signals = []

    for signal in history:
        if not signal.get("outcome_complete", False):
            continue

        if signal.get("outcome_error"):
            continue

        if signal.get("max_change_60m") is None:
            continue

        completed_signals.append(signal)

    return completed_signals

def analyze_overall(signals): 
    if not signals: 
        print("No completed signals to analyze.") 
        return

    max_changes = [
        signal["max_change_60m"]
        for signal in signals
        if signal.get("max_change_60m") is not None
    ]

    min_changes = [
        signal["min_change_60m"]
        for signal in signals
        if signal.get("min_change_60m") is not None
    ]

    avg_max_change = sum(max_changes) / len(max_changes)
    avg_min_change = sum(min_changes) / len(min_changes)

    median_max_change = statistics.median(max_changes)
    median_min_change = statistics.median(min_changes)

    print("\n===== PRE-MOVE ANALYZER =====")
    print(f"Completed signals: {len(signals)}")
    print(f"Average MAX 60m: {avg_max_change:+.2f}%")
    print(f"Average MIN 60m: {avg_min_change:+.2f}%")
    print(f"Median MAX 60m: {median_max_change:+.2f}%")
    print(f"Median MIN 60m: {median_min_change:+.2f}%")

def analyze_hit_rate(signals): 
    if not signals: 
        return

    thresholds = [1, 2, 3, 5]

    print("\n===== HIT RATE =====")

    for threshold in thresholds:
        hits = sum(
            1
            for signal in signals
            if signal.get("max_change_60m") is not None
            and signal["max_change_60m"] >= threshold
        )

        hit_rate = (hits / len(signals)) * 100

        print(
            f"+{threshold}%: "
            f"{hits}/{len(signals)} signals "
            f"({hit_rate:.1f}%)"
        )

def analyze_by_score(signals): 
    if not signals: 
        return
    scores = sorted(
        set(
            signal["pre_move_score"]
            for signal in signals
            if signal.get("pre_move_score") is not None
        )
    )

    print("\n===== RESULTS BY PRE-MOVE SCORE =====")

    for score in scores:
        group = [
            signal
            for signal in signals
            if signal.get("pre_move_score") == score
        ]
    
        if not group:
            continue

        avg_max = sum(
            signal["max_change_60m"]
            for signal in group
        ) / len(group)

        avg_min = sum(
            signal["min_change_60m"]
            for signal in group
        ) / len(group)

        hits_2 = sum(
            1
            for signal in group
            if signal["max_change_60m"] >= 2
        )

        hit_rate_2 = (hits_2 / len(group)) * 100

        print(
            f"Score {score}/10 | "
            f"Signals: {len(group)} | "
            f"Avg MAX: {avg_max:+.2f}% | "
            f"Avg MIN: {avg_min:+.2f}% | "
            f"+2% Hit Rate: {hit_rate_2:.1f}%"
        )

def analyze_component(signals, component): 
    groups = {}

    for signal in signals:
        value = signal.get(component)

        if value is None:
            continue

        groups.setdefault(value, []).append(signal)

    print(f"\n===== {component.upper()} =====")

    for value in sorted(groups):
        group = groups[value]

        max_changes = [
            signal["max_change_60m"]
            for signal in group
            if signal.get("max_change_60m") is not None
        ]

        min_changes = [
            signal["min_change_60m"]
            for signal in group
            if signal.get("min_change_60m") is not None
        ]

        if not max_changes or not min_changes:
            continue

        avg_max = sum(max_changes) / len(max_changes)
        avg_min = sum(min_changes) / len(min_changes)

        hits_2 = sum(
            1
            for signal in group
            if signal.get("max_change_60m") is not None
            and signal["max_change_60m"] >= 2
        )

        hit_rate_2 = (hits_2 / len(group)) * 100

        print(
            f"{component}={value} | "
            f"Signals: {len(group)} | "
            f"Avg MAX: {avg_max:+.2f}% | "
            f"Avg MIN: {avg_min:+.2f}% | "
            f"+2% Hit Rate: {hit_rate_2:.1f}%"
        )

def show_extreme_signals(signals, limit=5): 
    if not signals: 
        return

    sorted_by_max = sorted(
        signals,
        key=lambda signal: signal.get("max_change_60m", 0),
        reverse=True,
    )

    sorted_by_min = sorted(
        signals,
        key=lambda signal: signal.get("min_change_60m", 0),
    )

    print("\n===== TOP SIGNALS =====")

    for signal in sorted_by_max[:limit]:
        print(
            f"{signal['symbol']} | "
            f"Score: {signal['pre_move_score']}/10 | "
            f"Price: {signal['price_score']} | "
            f"Volume: {signal['volume_score']} | "
            f"OI: {signal['oi_score']} | "
            f"Distance: {signal['distance_score']} | "
            f"MAX: {signal['max_change_60m']:+.2f}% | "
            f"MIN: {signal['min_change_60m']:+.2f}%"
        )

    print("\n===== WORST SIGNALS =====")

    for signal in sorted_by_min[:limit]:
        print(
            f"{signal['symbol']} | "
            f"Score: {signal['pre_move_score']}/10 | "
            f"Price: {signal['price_score']} | "
            f"Volume: {signal['volume_score']} | "
            f"OI: {signal['oi_score']} | "
            f"Distance: {signal['distance_score']} | "
            f"MAX: {signal['max_change_60m']:+.2f}% | "
            f"MIN: {signal['min_change_60m']:+.2f}%"
        )

def analyze_quality_hits(signals): 
    if not signals: 
        return

    target = 2
    max_drawdown = -2

    quality_hits = [
        signal
        for signal in signals
        if signal.get("max_change_60m") is not None
        and signal.get("min_change_60m") is not None
        and signal["max_change_60m"] >= target
        and signal["min_change_60m"] > max_drawdown
    ]

    quality_hit_rate = (
        len(quality_hits) / len(signals)
    ) * 100

    print("\n===== QUALITY HIT RATE =====")
    print(f"Target: +{target}%")
    print(f"Max allowed drawdown: {max_drawdown}%")
    print(
        f"Quality hits: "
        f"{len(quality_hits)}/{len(signals)} "
        f"({quality_hit_rate:.1f}%)"
    )

def analyze_quality_by_score(signals): 
    if not signals: 
        return

    target = 2
    max_drawdown = -2

    scores = sorted(
        set(
            signal["pre_move_score"]
            for signal in signals
            if signal.get("pre_move_score") is not None
        )
    )

    print("\n===== QUALITY HIT RATE BY SCORE =====")

    for score in scores:
        group = [
           signal
           for signal in signals
           if signal.get("pre_move_score") == score
        ]

        quality_hits = [
            signal
            for signal in group
            if signal.get("max_change_60m") is not None
            and signal.get("min_change_60m") is not None
            and signal["max_change_60m"] >= target
            and signal["min_change_60m"] > max_drawdown
        ]

        quality_hit_rate = (
            len(quality_hits) / len(group)
        ) * 100

        print(
            f"Score {score}/10 | "
            f"Quality Hits: {len(quality_hits)}/{len(group)} "
            f"({quality_hit_rate:.1f}%)"
        )

if __name__ == "__main__":
    signals = load_completed_signals()

    analyze_overall(signals)
    analyze_hit_rate(signals)
    analyze_by_score(signals)

    analyze_component(signals, "price_score")
    analyze_component(signals, "volume_score")
    analyze_component(signals, "oi_score")
    analyze_component(signals, "distance_score")
    analyze_component(signals, "confluence_score")
    analyze_quality_hits(signals)
    analyze_quality_by_score(signals)
    show_extreme_signals(signals)