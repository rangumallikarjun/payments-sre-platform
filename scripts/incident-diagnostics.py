#!/usr/bin/env python3
"""Consolidated incident triage report for a single service.

Pulls recent error-rate and latency data from Prometheus, plus recent pod
restarts/events from Kubernetes, into one report — the first thing you'd
want during an incident instead of tabbing between dashboards and `kubectl`.

Usage:
    python incident-diagnostics.py payment-service \
        --prometheus-url http://localhost:9090 \
        --namespace payments
"""
import argparse
import subprocess
import sys

import requests

METRIC_BY_SERVICE = {
    "payment-service": "payment_requests_total",
    "fraud-monitor": "fraud_score_requests_total",
    "notification-service": "notification_requests_total",
}


def query_prometheus(base_url: str, query: str):
    resp = requests.get(f"{base_url}/api/v1/query", params={"query": query}, timeout=10)
    resp.raise_for_status()
    return resp.json()["data"]["result"]


def print_error_rate(base_url: str, service: str, window: str):
    metric = METRIC_BY_SERVICE.get(service)
    if not metric:
        print(f"Unknown service '{service}', skipping Prometheus checks")
        return

    query = f'sum(rate({metric}{{status=~"error|failed"}}[{window}])) / sum(rate({metric}[{window}]))'
    result = query_prometheus(base_url, query)
    if not result:
        print(f"  no error-rate data for {service} over {window}")
        return
    rate = float(result[0]["value"][1])
    print(f"  error rate over {window}: {rate * 100:.2f}%")


def print_pod_status(namespace: str, service: str):
    print(f"\nPod status (kubectl -n {namespace} get pods -l app={service}):")
    try:
        subprocess.run(
            ["kubectl", "-n", namespace, "get", "pods", "-l", f"app={service}"],
            check=False,
        )
    except FileNotFoundError:
        print("  kubectl not found — skipping cluster checks (are you running against Docker Compose only?)")
        return

    print(f"\nRecent restarts / warning events for {service}:")
    subprocess.run(
        [
            "kubectl", "-n", namespace, "get", "events",
            "--field-selector", f"involvedObject.name={service}",
            "--sort-by", ".lastTimestamp",
        ],
        check=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("service", choices=list(METRIC_BY_SERVICE.keys()))
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--namespace", default="payments")
    parser.add_argument("--window", default="10m")
    args = parser.parse_args()

    print(f"=== Incident triage report: {args.service} ===\n")
    print(f"Metrics (Prometheus @ {args.prometheus_url}):")
    try:
        print_error_rate(args.prometheus_url, args.service, args.window)
    except requests.RequestException as exc:
        print(f"  could not reach Prometheus: {exc}")

    print_pod_status(args.namespace, args.service)


if __name__ == "__main__":
    sys.exit(main())
