# Observability stack

All free/open-source, run via `docker compose up` from the repo root.

| Component | Purpose | URL (local) |
|---|---|---|
| Prometheus | Scrapes `/metrics` from each service, evaluates alert rules | http://localhost:9090 |
| Grafana | Dashboards over Prometheus data | http://localhost:3000 (admin/admin) |
| OpenTelemetry Collector | Receives traces from each service via OTLP | grpc :4317 / http :4318 |

## What to look at

- `prometheus/prometheus.yml` — scrape targets for the three services.
- `prometheus/alert-rules.yml` — SLO-driven alerts (error rate, p95 latency)
  tied to the budgets in [../sli-slo/slo-definitions.yaml](../sli-slo/slo-definitions.yaml).
- `grafana/dashboards/service-overview.json` — RED-metrics dashboard,
  auto-provisioned on Grafana startup.
- `otel-collector-config.yaml` — receives OTLP traces from each service and
  logs them (swap the `logging` exporter for a real backend like
  Jaeger/Tempo if you want to view traces visually — both have free
  self-hosted options).

## Generating traffic to see it work

With the stack running (`docker compose up`), generate some load:

```bash
for i in {1..200}; do
  curl -s -X POST http://localhost:8001/payments \
    -H "Content-Type: application/json" \
    -d '{"amount_cents": 1200, "merchant_id": "m-1"}' > /dev/null
done
```

Then open Grafana and watch the `payment_requests_total` rate and latency
panels update, and check Prometheus's Alerts page as you push the synthetic
`FAILURE_RATE` env var higher to trip `PaymentServiceHighErrorRate`.
