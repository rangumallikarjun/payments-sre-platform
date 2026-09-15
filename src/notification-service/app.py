"""Synthetic notification-service.

Simulates sending a payment confirmation, with an injected random-failure
rate used to exercise alerting rules and error-budget tracking. Sends no
real notifications.
"""
import os
import random
import time

from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel

SERVICE_NAME = "notification-service"
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.04"))

app = FastAPI(title=SERVICE_NAME)
app.mount("/metrics", make_asgi_app())

NOTIFY_COUNT = Counter(
    "notification_requests_total", "Total notification attempts", ["status"]
)
NOTIFY_LATENCY = Histogram(
    "notification_duration_seconds", "Notification send latency"
)


class NotifyRequest(BaseModel):
    payment_id: str
    channel: str = "email"


class NotifyResult(BaseModel):
    payment_id: str
    channel: str
    delivered: bool


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/readyz")
def readyz():
    return {"status": "ready", "service": SERVICE_NAME}


@app.post("/notify", response_model=NotifyResult)
def send_notification(req: NotifyRequest):
    start = time.time()
    time.sleep(max(0.0, random.gauss(50, 15)) / 1000)

    if random.random() < FAILURE_RATE:
        NOTIFY_COUNT.labels(status="failed").inc()
        NOTIFY_LATENCY.observe(time.time() - start)
        raise HTTPException(status_code=502, detail="synthetic delivery provider error")

    NOTIFY_COUNT.labels(status="delivered").inc()
    NOTIFY_LATENCY.observe(time.time() - start)
    return NotifyResult(payment_id=req.payment_id, channel=req.channel, delivered=True)
