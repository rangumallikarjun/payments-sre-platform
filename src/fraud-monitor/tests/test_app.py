import os

os.environ["FAILURE_RATE"] = "0"
os.environ["FLAG_RATE"] = "0"

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200


def test_score_payment_clear():
    resp = client.post(
        "/score",
        json={"payment_id": "p-1", "amount_cents": 2500, "merchant_id": "m-1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["flagged"] is False
    assert 0.0 <= body["risk_score"] <= 1.0
