"""Synthetic fraud-monitor.

Scores incoming payment events against simple synthetic rules. Exists to
generate realistic traffic/failure patterns for the observability tooling in
this repo — it implements no real fraud detection.
"""
import os
import random
import time

from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel

SERVICE_NAME = "fraud-monitor"
FLAG_RATE = float(os.getenv("FLAG_RATE", "0.05"))
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.02"))

app = FastAPI(title=SERVICE_NAME)
app.mount("/metrics", make_asgi_app())

SCORE_COUNT = Counter(
    "fraud_score_requests_total", "Total fraud scoring requests", ["outcome"]
)
SCORE_LATENCY = Histogram(
    "fraud_score_duration_seconds", "Fraud scoring latency"
)


class ScoreRequest(BaseModel):
    payment_id: str
    amount_cents: int
    merchant_id: str


class ScoreResult(BaseModel):
    payment_id: str
    risk_score: float
    flagged: bool


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/readyz")
def readyz():
    return {"status": "ready", "service": SERVICE_NAME}


@app.post("/score", response_model=ScoreResult)
def score_payment(req: ScoreRequest):
    start = time.time()
    time.sleep(max(0.0, random.gauss(30, 10)) / 1000)

    if random.random() < FAILURE_RATE:
        SCORE_COUNT.labels(outcome="error").inc()
        SCORE_LATENCY.observe(time.time() - start)
        raise HTTPException(status_code=503, detail="synthetic scoring engine timeout")

    flagged = random.random() < FLAG_RATE
    risk_score = round(random.uniform(0.7, 0.99) if flagged else random.uniform(0.0, 0.3), 3)

    SCORE_COUNT.labels(outcome="flagged" if flagged else "clear").inc()
    SCORE_LATENCY.observe(time.time() - start)
    return ScoreResult(payment_id=req.payment_id, risk_score=risk_score, flagged=flagged)
