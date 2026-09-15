"""Synthetic payment-service.

Simulates accepting and validating a payment request. Exists purely to
generate realistic traffic, latency, and failure patterns for the
observability and reliability tooling in this repo. It does not process real
payments or money.
"""
import os
import random
import time
import uuid

from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel

SERVICE_NAME = "payment-service"
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.03"))
LATENCY_MS_MEAN = float(os.getenv("LATENCY_MS_MEAN", "80"))

app = FastAPI(title=SERVICE_NAME)
app.mount("/metrics", make_asgi_app())

REQUEST_COUNT = Counter(
    "payment_requests_total", "Total payment requests", ["status"]
)
REQUEST_LATENCY = Histogram(
    "payment_request_duration_seconds", "Payment request latency"
)


class PaymentRequest(BaseModel):
    amount_cents: int
    currency: str = "USD"
    merchant_id: str


class PaymentResult(BaseModel):
    payment_id: str
    status: str


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/readyz")
def readyz():
    return {"status": "ready", "service": SERVICE_NAME}


@app.post("/payments", response_model=PaymentResult)
def create_payment(req: PaymentRequest):
    start = time.time()
    # Simulate variable downstream latency.
    time.sleep(max(0.0, random.gauss(LATENCY_MS_MEAN, LATENCY_MS_MEAN / 4)) / 1000)

    if req.amount_cents <= 0:
        REQUEST_COUNT.labels(status="rejected").inc()
        REQUEST_LATENCY.observe(time.time() - start)
        raise HTTPException(status_code=400, detail="amount_cents must be positive")

    if random.random() < FAILURE_RATE:
        REQUEST_COUNT.labels(status="error").inc()
        REQUEST_LATENCY.observe(time.time() - start)
        raise HTTPException(status_code=500, detail="synthetic downstream failure")

    REQUEST_COUNT.labels(status="success").inc()
    REQUEST_LATENCY.observe(time.time() - start)
    return PaymentResult(payment_id=str(uuid.uuid4()), status="accepted")
