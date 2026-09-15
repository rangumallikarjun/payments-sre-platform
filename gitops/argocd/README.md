# Argo CD (GitOps entry point)

This is the GitOps control point: once applied, Argo CD continuously
reconciles the live cluster to match `k8s/base/` in this repository.
Manual `kubectl apply`/`kubectl edit` against the `payments` namespace stops
being the source of truth — commits do.

## Install Argo CD (local kind/minikube cluster)

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for it to come up
kubectl -n argocd rollout status deploy/argocd-server

# Access the UI (separate terminal)
kubectl -n argocd port-forward svc/argocd-server 8080:443

# Get the initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Open https://localhost:8080, log in as `admin` with the password above.

## Register this project + application

1. Fork/push this repo to your own GitHub account.
2. Edit `app-payments-platform.yaml` and replace `YOUR_GITHUB_USERNAME` with
   your GitHub username (or point `repoURL` at your fork).
3. Apply both manifests:

```bash
kubectl apply -f project.yaml
kubectl apply -f app-payments-platform.yaml
```

Argo CD will clone the repo, sync `k8s/base/`, and from then on auto-sync +
self-heal (`syncPolicy.automated`) any drift or new commits — this is the
"safe, GitOps-driven deployment" workflow referenced throughout the project.

## Promoting a change

1. Edit a manifest under `k8s/base/` (e.g. bump `replicas`, change an image
   tag after CI publishes a new one).
2. Commit and push to `main`.
3. Argo CD detects the diff and rolls it out automatically. Rolling back is
   `git revert` + push.
