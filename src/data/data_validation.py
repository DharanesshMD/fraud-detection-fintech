from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float = Field(..., gt=0)
    currency: str
    timestamp: datetime
    merchant_id: Optional[str] = None
    location: Optional[str] = None
    card_id: Optional[str] = None
    merchant_category: Optional[str] = None

    @validator("timestamp", pre=True)
    def parse_timestamp(cls, v):
        if isinstance(v, datetime):
            return v
        # accept numeric (epoch) or ISO strings
        try:
            if isinstance(v, (int, float)):
                return datetime.fromtimestamp(v)
            return datetime.fromisoformat(v)
        except Exception:
            raise ValueError("timestamp must be ISO8601 string or epoch")


def validate_transaction(obj: dict) -> Transaction:
    """Validate and return a Transaction object from a dict-like object.

    Raises pydantic.ValidationError on invalid input.
    """
    return Transaction(**obj)
