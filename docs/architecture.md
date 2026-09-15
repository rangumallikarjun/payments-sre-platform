# Architecture

## Goals

Simulate the SRE/platform concerns of operating a real-time payments system:
reliability targets, safe delivery, and fast detection/response — using a
minimal but realistic set of services.

## Services

Three synthetic FastAPI services stand in for a payments pipeline:

- **payment-service** — accepts a synthetic payment request, validates it,
  and emits a result. Exposes Prometheus metrics (request count, latency,
  error rate) and OpenTelemetry traces.
- **fraud-monitor** — consumes payment events and scores them against simple
  synthetic rules, occasionally flagging/rejecting to simulate real
  variability in downstream dependencies.
- **notification-service** — simulates sending a confirmation, with an
  injected random-failure rate used to exercise alerting and error budgets.

None of these move real money or contain real payment logic — they exist only
to produce realistic traffic, latency, and failure patterns to operate
against.

## Delivery pipeline (CI)

`.github/workflows/ci.yml` runs on every push/PR:

1. Install dependencies, run unit tests for each service.
2. Build a Docker image per service.
3. Scan each image with Trivy; fail the build on high/critical CVEs.
4. (On `main`) push images to GitHub Container Registry (GHCR).

## Delivery pipeline (CD / GitOps)

Kubernetes manifests live under `k8s/base/`. Argo CD (defined in
`gitops/argocd/`) watches this repository and continuously reconciles the
cluster to match what's committed — no manual `kubectl apply` in normal
operation, no direct cluster edits. Rolling back a bad deploy means reverting
a Git commit.

## Infrastructure as Code

`terraform/azure/` defines an AKS cluster, its node pool, a Log Analytics
workspace for monitoring, and an Azure Key Vault for secrets — the Azure
building blocks referenced by the JD (AKS, monitoring, networking, security).
It's written to `terraform plan` cleanly; you don't need to `apply` it (which
costs money) to demonstrate the IaC approach.

## Observability

- **Metrics**: each service exposes a `/metrics` endpoint (Prometheus
  client). Prometheus scrapes them; Grafana dashboards visualize RED metrics
  (Rate, Errors, Duration).
- **Traces**: each service is instrumented with the OpenTelemetry SDK,
  exporting to an OpenTelemetry Collector, which can fan out to any tracing
  backend (Jaeger/Tempo/etc. — kept out of scope here to stay free/minimal).
- **Alerting**: `observability/prometheus/alert-rules.yml` defines alerts for
  elevated error rate and latency breaches tied to the SLOs below.

## Reliability engineering

`sli-slo/slo-definitions.yaml` defines SLOs per service (e.g. 99.5%
availability, p95 latency budget). `sli-slo/error_budget.py` reads Prometheus
query results and computes remaining error budget — the same mechanic used in
production SRE practice to decide "can we ship, or do we need to freeze and
fix reliability first."

## DevSecOps guardrails

`policy/conftest/` contains Rego policies that fail CI if a Kubernetes
manifest is missing resource requests/limits, runs as root, or omits
liveness/readiness probes — cheap, automated production-readiness checks
enforced before merge.

## Incident response tooling

`scripts/incident-diagnostics.py` is a lightweight triage tool: given a
service name, it queries Prometheus for the last N minutes of error rate and
latency, and `kubectl` for recent pod restarts/events, and prints a single
consolidated report — the first thing you'd want during an incident instead
of tabbing between five dashboards.
