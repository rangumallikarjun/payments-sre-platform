# Operational scripts

| Script | Purpose |
|---|---|
| `health-check.sh` / `health-check.ps1` | Sweeps `/healthz` and `/readyz` across all three services (Docker Compose setup). Bash and PowerShell versions, per the JD's scripting requirement. |
| `deploy-validate.sh` | Post-deploy gate: waits for every Deployment in a namespace to roll out successfully and surfaces recent warning events. Run after an Argo CD sync. |
| `incident-diagnostics.py` | Single-command incident triage: recent Prometheus error rate for a service plus `kubectl` pod status/events, in one report. |

## Usage

```bash
# Docker Compose stack running locally
./scripts/health-check.sh
# or on Windows
powershell -File scripts/health-check.ps1

# Against a real cluster after a deploy
./scripts/deploy-validate.sh payments 120

# During an incident
python scripts/incident-diagnostics.py payment-service --prometheus-url http://localhost:9090
```
