from typing import Iterable, Any
import json

from src.data.kafka_consumer import KafkaProcessor
from src.models.dummy_model import DummyModel
from src.decision_engine.rules_engine import decide


def run_stream(iterator: Iterable[Any], kafka_cfg_path: str = None, feature_cfg_path: str = None, result_hook=None):
    """Run KafkaProcessor over iterator and forward predictions to decision engine.

    result_hook, if provided, will be called with the final decision dict.
    """
    # We don't require config files here; use the processor factory for convenience
    processor = KafkaProcessor.from_config(kafka_cfg_path or "configs/kafka_config.yaml", feature_cfg_path or "configs/feature_config.yaml")
    model = DummyModel()
    model.load(None)

    def local_hook(processed: dict):
        features = processed.get("features", {})
        score = float(model.predict({**features, "customer_id": processed.get("customer_id"), "transaction_id": processed.get("transaction_id")}))
        decision = decide(score, features)
        out = {"transaction_id": processed.get("transaction_id"), "fraud_score": score, "decision": decision}
        if result_hook:
            result_hook(out)
        else:
            print(json.dumps(out))

    processor.process_iterator(iterator, result_hook=local_hook)
