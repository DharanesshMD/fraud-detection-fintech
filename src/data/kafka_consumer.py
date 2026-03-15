"""A small, testable Kafka consumer prototype.

This module intentionally separates message iteration from processing so unit
and integration tests can supply mocked messages without needing a running
Kafka cluster. For real deployments the "connect_and_iter" can be implemented
using aiokafka or confluent-kafka-python.
"""
import json
from typing import Iterable, Callable, Any
import yaml

from .data_validation import validate_transaction
from .feature_engineering import compute_velocity_features
from .cache import make_cache


class KafkaProcessor:
    def __init__(self, cache_cfg: dict, feature_cfg: dict):
        self.cache = make_cache(cache_cfg)
        self.feature_cfg = feature_cfg

    def process_message(self, raw: Any) -> dict:
        """Parse raw message (JSON string or dict), validate, compute features."""
        if isinstance(raw, (bytes, str)):
            obj = json.loads(raw)
        elif isinstance(raw, dict):
            obj = raw
        else:
            raise TypeError("Unsupported message type")

        tx = validate_transaction(obj)
        features = compute_velocity_features(tx, self.cache, self.feature_cfg)
        return {"transaction_id": tx.transaction_id, "customer_id": tx.customer_id, "features": features}

    def process_iterator(self, iterator: Iterable[Any], result_hook: Callable[[dict], None] = None):
        """Consume messages from a generic iterator and apply processing.

        result_hook, if provided, is called with the output dict for each message.
        """
        for raw in iterator:
            try:
                out = self.process_message(raw)
                if result_hook:
                    result_hook(out)
                else:
                    print(json.dumps(out))
            except Exception as e:
                # In production we would have structured logging and retry policies
                print(f"Failed to process message: {e}")


def load_yaml(path: str) -> dict:
    with open(path, "r") as fh:
        return yaml.safe_load(fh)


def from_config(kafka_config_path: str, feature_config_path: str) -> KafkaProcessor:
    kafka_cfg = load_yaml(kafka_config_path)
    feature_cfg = load_yaml(feature_config_path)
    cache_cfg = kafka_cfg.get("cache", {"driver": "memory"})
    return KafkaProcessor(cache_cfg=cache_cfg, feature_cfg=feature_cfg)
