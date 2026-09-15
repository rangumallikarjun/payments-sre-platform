# SLIs, SLOs, and error budgets

`slo-definitions.yaml` declares, per service, what's measured (the SLI), the
target (the SLO), and the Prometheus query used to compute it.

`error_budget.py` queries a running Prometheus instance and reports how much
of each service's error budget has been consumed over a given window —
useful both as a CLI you run during an incident and as a script you could
wire into CI to gate risky deploys when a budget is already exhausted.

## Usage

```bash
pip install -r requirements.txt
python error_budget.py --prometheus-url http://localhost:9090 --window 1h
```

Example output:

```
[payment-service/availability] actual=0.9820 target=0.9950 error_budget_consumed=360.0% status=EXHAUSTED
[fraud-monitor/availability] actual=0.9910 target=0.9900 error_budget_consumed=0.0% status=OK
[notification-service/delivery_success] actual=0.9640 target=0.9700 error_budget_consumed=200.0% status=EXHAUSTED
```

An `EXHAUSTED` status is the same signal a real SRE team uses to decide:
freeze feature work, prioritize reliability fixes, and treat the next
incident review as mandatory.
