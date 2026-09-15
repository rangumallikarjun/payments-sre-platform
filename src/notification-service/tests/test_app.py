import os

os.environ["FAILURE_RATE"] = "0"

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200


def test_send_notification_delivered():
    resp = client.post("/notify", json={"payment_id": "p-1", "channel": "email"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["delivered"] is True
