#!/usr/bin/env bash
# Pre/post-deploy validation gate for the payments namespace. Intended to run
# after an Argo CD sync (or a manual kubectl apply) to confirm the rollout is
# actually healthy before calling a deploy "done."
#
# Usage: ./deploy-validate.sh [namespace] [timeout_seconds]
set -euo pipefail

NAMESPACE="${1:-payments}"
TIMEOUT="${2:-120}"

deployments=$(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

if [ -z "$deployments" ]; then
  echo "No deployments found in namespace '$NAMESPACE'"
  exit 1
fi

failed=0

for dep in $deployments; do
  echo "Waiting for rollout: $dep"
  if kubectl rollout status "deployment/$dep" -n "$NAMESPACE" --timeout="${TIMEOUT}s"; then
    echo "OK    $dep rolled out successfully"
  else
    echo "FAIL  $dep did not become ready within ${TIMEOUT}s"
    failed=$((failed + 1))
  fi
done

echo "---"
echo "Recent warning events in namespace '$NAMESPACE':"
kubectl get events -n "$NAMESPACE" --field-selector type=Warning --sort-by=.lastTimestamp | tail -n 10

if [ "$failed" -gt 0 ]; then
  echo "$failed deployment(s) failed validation"
  exit 1
fi

echo "All deployments validated successfully"
