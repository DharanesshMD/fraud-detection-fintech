from src.decision_engine.rules_engine import decide


def test_decide_default_thresholds():
    out = decide(0.1, {})
    assert out["decision"] == "APPROVE"

    out = decide(0.6, {})
    assert out["decision"] == "REVIEW"

    out = decide(0.9, {})
    assert out["decision"] == "DECLINE"
