from typing import Any, Dict


class ModelInterface:
    """Minimal model interface expected by the API and pipeline.

    Implementations should provide a deterministic load(path) and predict(features) method.
    """

    def load(self, path: str | None) -> None:
        raise NotImplementedError

    def predict(self, features: Dict[str, Any]) -> float:
        raise NotImplementedError
