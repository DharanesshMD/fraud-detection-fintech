import math
from typing import Dict, Any
from .interface import ModelInterface


class DummyModel(ModelInterface):
    """A tiny deterministic "model" used for development and integration tests.

    The predict method maps a small set of velocity features into a 0..1 score.
    This keeps the API and decision engine testable without heavy ML deps.
    """

    def load(self, path: str | None) -> None:
        # No-op for dummy model; in real models we'd load parameters from `path`
        self._meta = {"name": "dummy"}

    def predict(self, features: Dict[str, Any]) -> float:
        # Combine a couple of known feature names if present to create a score.
        # This is intentionally simple and deterministic.
        sum_24h = float(features.get("txn_sum_amount_24h", 0.0))
        count_24h = float(features.get("txn_count_24h", 0.0))

        # basic heuristic: larger sums and counts increase fraud score
        # normalize by a simple scale to keep score in 0..1
        score = (sum_24h / 1000.0) + (count_24h * 0.02)
        # squash into 0..1
        score = 1.0 - math.exp(-score)
        if score < 0:
            score = 0.0
        if score > 1:
            score = 1.0
        return score
