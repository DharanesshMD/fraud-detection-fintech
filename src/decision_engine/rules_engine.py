from typing import Dict, Any


def decide(score: float, features: Dict[str, Any], cfg: Dict[str, Any] = None) -> Dict[str, Any]:
    """Return a decision dict based on score and simple configurable thresholds.

    Decision fields: decision (APPROVE/REVIEW/DECLINE), reason
    """
    if cfg is None:
        cfg = {"decline_threshold": 0.8, "review_threshold": 0.5}

    if score >= cfg.get("decline_threshold", 0.8):
        return {"decision": "DECLINE", "reason": "score_threshold"}
    if score >= cfg.get("review_threshold", 0.5):
        return {"decision": "REVIEW", "reason": "score_threshold"}
    return {"decision": "APPROVE", "reason": "score_threshold"}
