import os

os.environ["FAILURE_RATE"] = "0"
os.environ["LATENCY_MS_MEAN"] = "1"

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_payment_success():
    resp = client.post(
        "/payments",
        json={"amount_cents": 1500, "currency": "USD", "merchant_id": "m-1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "accepted"
    assert "payment_id" in body


def test_create_payment_rejects_non_positive_amount():
    resp = client.post(
        "/payments",
        json={"amount_cents": 0, "currency": "USD", "merchant_id": "m-1"},
    )
    assert resp.status_code == 400
