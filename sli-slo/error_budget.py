#!/usr/bin/env python3
"""Compute error-budget consumption for each service in slo-definitions.yaml
against a running Prometheus instance.

Usage:
    python error_budget.py --prometheus-url http://localhost:9090 --window 1h

For each availability SLI, this queries the *actual* success ratio over the
window, compares it to the target in slo-definitions.yaml, and reports how
much of the error budget has been consumed. This is the same mechanic used
in production SRE practice to decide whether a team can keep shipping
features or needs to pause and invest in reliability.
"""
import argparse
import sys

import requests
import yaml


def load_definitions(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def query_prometheus(base_url: str, query: str) -> float | None:
    resp = requests.get(f"{base_url}/api/v1/query", params={"query": query}, timeout=10)
    resp.raise_for_status()
    result = resp.json()["data"]["result"]
    if not result:
        return None
    return float(result[0]["value"][1])


def evaluate(base_url: str, window: str, definitions: dict) -> int:
    exit_code = 0
    for service in definitions["services"]:
        for sli in service["slis"]:
            if "slo_target" not in sli:
                continue  # skip latency-style SLIs here; ratio SLIs only

            query = sli["prometheus_query"].format(window=window)
            actual = query_prometheus(base_url, query)
            target = sli["slo_target"]

            if actual is None:
                print(f"[{service['name']}/{sli['name']}] no data for window={window} (is traffic flowing?)")
                continue

            allowed_failure = 1 - target
            actual_failure = 1 - actual
            budget_consumed_pct = (actual_failure / allowed_failure * 100) if allowed_failure > 0 else 0.0

            status = "OK"
            if budget_consumed_pct >= 100:
                status = "EXHAUSTED"
                exit_code = 1
            elif budget_consumed_pct >= 80:
                status = "WARNING"

            print(
                f"[{service['name']}/{sli['name']}] "
                f"actual={actual:.4f} target={target:.4f} "
                f"error_budget_consumed={budget_consumed_pct:.1f}% status={status}"
            )
    return exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--window", default="1h", help="Prometheus range window, e.g. 1h, 30d")
    parser.add_argument("--definitions", default="slo-definitions.yaml")
    args = parser.parse_args()

    definitions = load_definitions(args.definitions)
    exit_code = evaluate(args.prometheus_url, args.window, definitions)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
