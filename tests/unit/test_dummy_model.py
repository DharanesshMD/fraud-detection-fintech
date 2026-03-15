from src.models.dummy_model import DummyModel


def test_dummy_model_predict_basic():
    model = DummyModel()
    model.load(None)
    features = {"txn_sum_amount_24h": 120.0, "txn_count_24h": 3}
    score = model.predict(features)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
