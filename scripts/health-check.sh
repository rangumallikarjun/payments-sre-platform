#!/usr/bin/env bash
# Quick health-check sweep across all services. Exits non-zero if any
# service fails its /healthz or /readyz check.
set -euo pipefail

declare -A SERVICES=(
  ["payment-service"]="http://localhost:8001"
  ["fraud-monitor"]="http://localhost:8002"
  ["notification-service"]="http://localhost:8003"
)

failures=0

for name in "${!SERVICES[@]}"; do
  base_url="${SERVICES[$name]}"
  for path in healthz readyz; do
    if curl -sf "${base_url}/${path}" > /dev/null; then
      echo "OK    ${name} /${path}"
    else
      echo "FAIL  ${name} /${path}"
      failures=$((failures + 1))
    fi
  done
done

if [ "$failures" -gt 0 ]; then
  echo "$failures check(s) failed"
  exit 1
fi

echo "All services healthy"
