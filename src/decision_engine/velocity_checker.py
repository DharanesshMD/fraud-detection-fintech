from typing import Dict, Any


def check_velocity(features: Dict[str, Any], cfg: Dict[str, Any] = None) -> Dict[str, Any]:
    """Simple velocity checks returning a dict of flags and explanations.

    Example rule: if txn_count_1h > cfg.max_txn_1h then flag.
    """
    if cfg is None:
        cfg = {"max_txn_1h": 5, "max_amount_24h": 1000.0}

    flags = []
    cnt_1h = int(features.get("txn_count_1h", 0))
    sum_24h = float(features.get("txn_sum_amount_24h", 0.0))

    if cnt_1h > cfg.get("max_txn_1h", 5):
        flags.append({"flag": "high_count_1h", "value": cnt_1h})
    if sum_24h > cfg.get("max_amount_24h", 1000.0):
        flags.append({"flag": "high_amount_24h", "value": sum_24h})

    return {"flags": flags}
