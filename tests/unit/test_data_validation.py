import pytest
from src.data.data_validation import validate_transaction
from pydantic import ValidationError
from datetime import datetime


def test_valid_transaction():
    obj = {
        "transaction_id": "tx_1",
        "customer_id": "cust_1",
        "amount": 12.5,
        "currency": "USD",
        "timestamp": datetime.utcnow().isoformat(),
    }
    tx = validate_transaction(obj)
    assert tx.transaction_id == "tx_1"
    assert tx.amount == 12.5


def test_invalid_transaction_missing_fields():
    obj = {"transaction_id": "tx_2", "amount": 5.0}
    with pytest.raises(ValidationError):
        validate_transaction(obj)


def test_invalid_amount_negative():
    obj = {
        "transaction_id": "tx_3",
        "customer_id": "cust_3",
        "amount": -1.0,
        "currency": "USD",
        "timestamp": datetime.utcnow().isoformat(),
    }
    with pytest.raises(ValidationError):
        validate_transaction(obj)
