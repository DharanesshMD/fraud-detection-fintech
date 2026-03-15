from fastapi.testclient import TestClient
from src.api.predict import app
from datetime import datetime

client = TestClient(app)


def make_payload():
    return {
        "transaction_id": "tx_api_1",
        "customer_id": "cust_api_1",
        "amount": 50.0,
        "currency": "USD",
        "timestamp": datetime.utcnow().isoformat(),
    }


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_predict_endpoint():
    payload = make_payload()
    r = client.post("/predict", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["transaction_id"] == payload["transaction_id"]
    assert "fraud_score" in data
    assert 0.0 <= data["fraud_score"] <= 1.0
    assert data["decision"] in {"APPROVE", "REVIEW", "DECLINE"}
    assert "explanation" in data
