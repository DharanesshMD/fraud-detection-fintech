from datetime import datetime, timedelta
import time
import json

from src.data.feature_engineering import compute_velocity_features
from src.data.data_validation import Transaction
from src.data.cache import InMemoryCache


def make_tx(tx_id: str, cust: str, amount: float, ts: datetime):
    return Transaction(
        transaction_id=tx_id,
        customer_id=cust,
        amount=amount,
        currency="USD",
        timestamp=ts,
    )


def test_velocity_features_simple():
    cache = InMemoryCache()
    now = datetime.utcnow()
    cfg = {"velocity_windows": {"1h": 3600, "24h": 86400}}

    # create two historical txns 30 and 90 minutes ago
    t1 = make_tx("t1", "c1", 10.0, now - timedelta(minutes=30))
    t2 = make_tx("t2", "c1", 5.0, now - timedelta(minutes=90))

    # process historical via direct zadd to simulate previous processing
    cache.zadd(f"cust:c1:txs:z", (t1.timestamp.timestamp()), json.dumps({"tx_id": t1.transaction_id, "amount": t1.amount, "ts": t1.timestamp.timestamp()}))
    cache.zadd(f"cust:c1:txs:z", (t2.timestamp.timestamp()), json.dumps({"tx_id": t2.transaction_id, "amount": t2.amount, "ts": t2.timestamp.timestamp()}))

    # new transaction now
    tx_new = make_tx("t3", "c1", 3.0, now)
    out = compute_velocity_features(tx_new, cache, cfg)

    # 1h window should include t1 and t3 -> count 2, sum 13.0
    assert out["txn_count_1h"] == 2
    assert abs(out["txn_sum_amount_1h"] - 13.0) < 1e-6

    # 24h window should include all three -> count 3, sum 18.0
    assert out["txn_count_24h"] == 3
    assert abs(out["txn_sum_amount_24h"] - 18.0) < 1e-6

    # aggregated counter should have been incremented (starts at 1)
    assert out["customer_total_txn_count"] >= 1
