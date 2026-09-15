# Kubernetes manifests

Plain Kubernetes manifests (no Helm/Kustomize dependency required) for the
three synthetic services. Apply them directly:

```bash
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/payment-service/ -f k8s/base/fraud-monitor/ -f k8s/base/notification-service/
```

Or let Argo CD manage them declaratively — see [../gitops/argocd](../gitops/argocd).

Each `deployment.yaml` points at the GHCR image path produced by the CI
workflow in `.github/workflows/ci.yml` (published as `:latest` and the commit
SHA on every push to `main`); the manifests pin `:initial` as a placeholder
tag until you push a real build and bump it.

Each Deployment sets resource requests/limits, a non-root security context,
and liveness/readiness probes intentionally — these are exactly the fields
the policy checks in [../policy/conftest](../policy/conftest) enforce.
