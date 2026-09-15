# Policy-as-code

[Conftest](https://www.conftest.dev/) (built on Open Policy Agent) checks
every Kubernetes manifest under `k8s/base/` against the Rego rules in
`conftest/deployment-guardrails.rego` before it can merge — these are the
DevSecOps/production-readiness guardrails referenced in the project's SRE
goals.

Checks enforced:

- Every container declares resource `requests` and `limits`.
- Every container sets `securityContext.runAsNonRoot: true`.
- Every container defines a `readinessProbe` and a `livenessProbe`.
- No container image uses the mutable `:latest` tag.

## Run locally

```bash
# Install conftest: https://www.conftest.dev/install/ (free, open source)
conftest test k8s/base --policy conftest --all-namespaces
```

This also runs automatically in CI — see the `policy-check` job in
[../.github/workflows/ci.yml](../.github/workflows/ci.yml).
