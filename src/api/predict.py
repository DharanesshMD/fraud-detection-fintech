from fastapi import FastAPI, HTTPException
from typing import Any, Dict
import yaml

from src.data.data_validation import validate_transaction
from src.data.feature_engineering import compute_velocity_features
from src.data.cache import make_cache
from src.models.dummy_model import DummyModel


app = FastAPI(title="Fraud Detection API")

# Load configs at import time for simplicity in this minimal implementation
try:
    with open("configs/feature_config.yaml", "r") as fh:
        FEATURE_CFG = yaml.safe_load(fh)
except Exception:
    FEATURE_CFG = {"velocity_windows": {"1h": 3600, "24h": 86400}}

try:
    with open("configs/kafka_config.yaml", "r") as fh:
        KAFKA_CFG = yaml.safe_load(fh)
except Exception:
    KAFKA_CFG = {"cache": {"driver": "memory"}}

CACHE = make_cache(KAFKA_CFG.get("cache", {"driver": "memory"}))
# Initialize model eagerly so TestClient requests work even if startup events are not run in some test setups
MODEL = DummyModel()
MODEL.load(None)

@app.on_event("startup")
def load_model() -> None:
    # no-op because we already loaded the model eagerly; kept for compatibility with lifecycle hooks
    return None


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: Dict[str, Any]):
    """Validate a transaction, compute features and return a fraud score + decision.

    Response JSON contains: transaction_id, fraud_score (0..1), decision, explanation
    """
    try:
        tx = validate_transaction(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    features = compute_velocity_features(tx, CACHE, FEATURE_CFG)
    # include some identifying fields so model implementations can use them if needed
    features_with_meta = {**features, "customer_id": tx.customer_id, "transaction_id": tx.transaction_id}

    score = float(MODEL.predict(features_with_meta))

    # simple threshold-based decisioning (stub)
    if score >= 0.8:
        decision = "DECLINE"
    elif score >= 0.5:
        decision = "REVIEW"
    else:
        decision = "APPROVE"

    return {
        "transaction_id": tx.transaction_id,
        "fraud_score": score,
        "decision": decision,
        "explanation": "thresholds: 0.8 decline, 0.5 review (stub)"
    }
