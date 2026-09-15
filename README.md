# Payments SRE & GitOps Platform

A self-contained Site Reliability Engineering portfolio project that simulates
operating a real-time payments platform on Kubernetes, with GitOps-driven
delivery, infrastructure as code, and full observability.

This is a **personal learning/portfolio project**. It does not represent, and
is not affiliated with, any employer or company. All service names, data, and
"payment" flows are synthetic and built purely to demonstrate SRE/DevOps/
Platform Engineering practices.

## Why this project exists

Reliable payment systems need four things working together: safe deployments,
strong observability, fast incident response, and infrastructure that's
reproducible from code. This repo implements all four end-to-end using only
free and open-source tooling, runnable entirely on a laptop.

## What's inside

| Area | What it demonstrates | Tech |
|---|---|---|
| Application | Three synthetic microservices (`payment-service`, `fraud-monitor`, `notification-service`) | Python, FastAPI, Docker |
| CI | Build, test, vulnerability scan, image publish | GitHub Actions, Trivy |
| GitOps / CD | Declarative, Git-driven Kubernetes deployments | Argo CD, Kubernetes manifests (Kustomize-style) |
| Infrastructure as Code | Reproducible cloud infra definition | Terraform (Azure AKS example) |
| Observability | Metrics, dashboards, tracing, alerting | Prometheus, Grafana, OpenTelemetry Collector |
| Reliability engineering | SLIs/SLOs and error-budget tracking | Custom Python error-budget calculator |
| DevSecOps | Policy-as-code checks on Kubernetes manifests | Conftest / OPA (Rego) |
| Operations | Health checks, deploy validation, incident diagnostics | Bash, PowerShell, Python |

## Architecture

```
Developer → GitHub → GitHub Actions (build/test/scan) → Container Registry
                                                              │
                                                              ▼
                                                          Argo CD  ← watches gitops/ in this repo
                                                              │
                                                              ▼
                                                  Kubernetes (AKS or local: kind/minikube)
                                                   ┌──────────┼───────────┐
                                                payment-service  fraud-monitor  notification-service
                                                              │
                                                              ▼
                                              OpenTelemetry Collector → Prometheus → Grafana
                                                              │
                                                       Alertmanager rules → Incident scripts
```

See [docs/architecture.md](docs/architecture.md) for the full breakdown.

## Repo layout

```
src/                Synthetic microservices (Python/FastAPI) + Dockerfiles
k8s/base/           Kubernetes manifests for each service
gitops/argocd/      Argo CD Application/Project definitions (GitOps entry point)
terraform/azure/    IaC for an Azure AKS cluster (example, not deployed by CI)
observability/      Prometheus, Grafana, OpenTelemetry Collector configs
sli-slo/            SLI/SLO definitions and error-budget calculator
scripts/            Health checks, deploy validation, incident diagnostics
policy/             Policy-as-code guardrails for Kubernetes manifests
.github/workflows/  CI pipeline (build, test, scan, publish)
```

## Running it locally (100% free)

Requirements: Docker Desktop, and optionally `kind`/`minikube` + `kubectl` +
Argo CD CLI if you want the full GitOps loop.

### 1. Run the services + observability stack with Docker Compose

```bash
docker compose up --build
```

This starts all three services plus Prometheus, Grafana, and the OpenTelemetry
Collector.

- Payment service: http://localhost:8001/docs
- Fraud monitor: http://localhost:8002/docs
- Notification service: http://localhost:8003/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (default admin/admin)

### 2. Run the full GitOps loop on a local Kubernetes cluster

```bash
kind create cluster --name payments-sre
kubectl create namespace payments
kubectl apply -f k8s/base/ -n payments

# install Argo CD (see gitops/argocd/README in this folder for details)
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f gitops/argocd/app-payments-platform.yaml
```

Argo CD then continuously reconciles the cluster state against the manifests
in `k8s/base/`.

### 3. Provision equivalent infrastructure on Azure (optional, costs money if left running)

```bash
cd terraform/azure
terraform init
terraform plan
terraform apply
```

See [terraform/azure/README.md](terraform/azure/README.md).

## Reliability practices demonstrated

- **SLIs/SLOs & error budgets** — defined in [sli-slo/slo-definitions.yaml](sli-slo/slo-definitions.yaml)
  and computed by [sli-slo/error_budget.py](sli-slo/error_budget.py).
- **Observability** — structured logs, RED metrics, and distributed traces
  wired through the OpenTelemetry Collector into Prometheus/Grafana.
- **Incident response** — [scripts/incident-diagnostics.py](scripts/incident-diagnostics.py)
  pulls recent error-rate spikes and pod restarts into a single triage report.
- **Deployment safety** — [scripts/deploy-validate.sh](scripts/deploy-validate.sh)
  runs pre-deploy health/readiness checks; [policy/conftest](policy/conftest)
  blocks manifests that skip resource limits or run as root.
- **DevSecOps** — Trivy scans container images for CVEs in CI before they can
  be promoted.

## Free tools used (no paid services required)

GitHub, GitHub Actions, Docker, Kubernetes (kind/minikube), Argo CD,
Terraform, Prometheus, Grafana, OpenTelemetry Collector, Trivy, Conftest/OPA,
Python, Bash, PowerShell.

## License

MIT — see [LICENSE](LICENSE).
