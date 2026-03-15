from datetime import datetime, timezone
from typing import Dict, Any
import json

from .data_validation import Transaction


def _ts_seconds(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def compute_velocity_features(tx: Transaction, cache, feature_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a small set of velocity features for the transaction's customer.

    Uses the provided cache abstraction to store and query recent transactions.
    feature_cfg should contain windows in seconds, e.g. {"velocity_1h": 3600}
    """
    customer = tx.customer_id
    ts = _ts_seconds(tx.timestamp)

    # keys
    zkey = f"cust:{customer}:txs:z"

    # store this txn as member (we'll keep JSON with amount to illustrate)
    member = json.dumps({"tx_id": tx.transaction_id, "amount": tx.amount, "ts": ts})
    cache.zadd(zkey, score=ts, member=member)

    out = {}

    # compute count and sum over configured velocity windows
    for name, window in feature_cfg.get("velocity_windows", {}).items():
        start = ts - int(window)
        results = cache.zrangebyscore(zkey, min_score=start, max_score=ts)
        # results are list of tuples (score, member) for Redis-like, or (score, member)
        amounts = []
        for score, m in results:
            try:
                payload = json.loads(m)
                amounts.append(float(payload.get("amount", 0)))
            except Exception:
                # if member stored differently, try to parse as float
                try:
                    amounts.append(float(m))
                except Exception:
                    continue
        out[f"txn_count_{name}"] = len(amounts)
        out[f"txn_sum_amount_{name}"] = sum(amounts)
        out[f"txn_avg_amount_{name}"] = (sum(amounts) / len(amounts)) if amounts else 0.0

    # basic customer aggregates (could be backed by separate keys)
    agg_key = f"cust:{customer}:agg:count"
    total_count = cache.incr(agg_key, amount=1)
    out["customer_total_txn_count"] = total_count

    return out
