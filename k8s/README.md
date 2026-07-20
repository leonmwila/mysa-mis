# Kubernetes Deployment Guide

This directory provides a Kustomize-based setup for local, staging, and production.

## Directory layout

- `base/`: Shared Kubernetes resources.
- `overlays/local/`: Minikube-focused defaults.
- `overlays/staging/`: Staging VM defaults.
- `overlays/production/`: Production VM defaults.

## 1) Local with Minikube

Start cluster and ingress:

```bash
minikube start --cpus=4 --memory=8192
minikube addons enable ingress
```

Build the image inside Minikube Docker and deploy local overlay:

```bash
eval "$(minikube -p minikube docker-env)"
docker build -t mysa-mis-odoo:local .
kubectl apply -k k8s/overlays/local
```

Map local DNS host (Linux):

```bash
echo "$(minikube ip) mysa.local" | sudo tee -a /etc/hosts
```

Then open `http://mysa.local`.

## 2) Staging VM (recommended: K3s)

Install K3s on the staging VM and use Traefik (default K3s ingress).

Deploy staging overlay:

```bash
kubectl apply -k k8s/overlays/staging
```

Before deploying, update:

- `k8s/overlays/staging/postgres-secret-patch.yaml`
- `k8s/overlays/staging/odoo-config-patch.yaml`
- `k8s/overlays/staging/ingress-patch.yaml` (host and TLS secret)
- `k8s/overlays/staging/kustomization.yaml` image owner

## 3) Production on K3s

Use K3s on production as well if the server already has the same app deployed there. K3s ships with Traefik by default, so the production overlay is configured for Traefik ingress on plain HTTP until you add TLS.

Deploy production overlay:

```bash
kubectl apply -k k8s/overlays/production
```

Before deploying, update:

- `k8s/overlays/production/postgres-secret-patch.yaml`
- `k8s/overlays/production/odoo-config-patch.yaml`
- `k8s/overlays/production/ingress-patch.yaml` (host)
- `k8s/overlays/production/kustomization.yaml` image owner

### Reusable Production Deploy Flow (GHCR SHA Tag)

Use this flow to promote a tested commit to production in any similar project:

1. Build and push image to GHCR from CI (tag format: `sha-<commit>`).
2. Point kubectl to the production kubeconfig.
3. Update deployment image to the immutable SHA tag.
4. Wait for rollout completion and verify running image.

```bash
# Use production kubeconfig explicitly (recommended)
KUBECONFIG=~/.kube/config-production kubectl cluster-info

# Deploy a specific immutable image tag
IMAGE_TAG=sha-<commit>
KUBECONFIG=~/.kube/config-production \
	kubectl -n mysa-mis set image deployment/odoo \
	odoo=ghcr.io/leonmwila/mysa-mis:${IMAGE_TAG}

# Verify rollout
KUBECONFIG=~/.kube/config-production \
	kubectl -n mysa-mis rollout status deployment/odoo --timeout=300s

# Verify the deployed image
KUBECONFIG=~/.kube/config-production \
	kubectl -n mysa-mis get deploy odoo \
	-o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

Notes:

- `minikube image build ...` is local-only and does not deploy to production.
- If kubeconfig uses `https://127.0.0.1:6443`, replace it with your VM/server IP or DNS.
- If `kustomize` is not installed, prefer `kubectl kustomize` when available.
- Using SHA tags avoids stale image pulls when `imagePullPolicy` is `IfNotPresent`.

## GitHub Container Registry and CI/CD

Two workflows are included:

- `.github/workflows/build-and-push-ghcr.yml`: builds and pushes image to GHCR.
- `.github/workflows/deploy-k8s.yml`: manual deploy to staging or production.

Required GitHub repository secrets:

- `KUBECONFIG_STAGING`: full kubeconfig content for staging cluster.
- `KUBECONFIG_PRODUCTION`: full kubeconfig content for production cluster.

The build workflow publishes tags including `sha-*`, `staging-latest`, and release tags.
Use the deploy workflow with an immutable `sha-*` tag for predictable rollouts.

## Ingress advice

- Local Minikube: NGINX ingress is simple and sufficient.
- Staging/Production on K3s: Traefik is a good default, and the production overlay should use `ingressClassName: traefik`.
- For TLS automation, add cert-manager with Let’s Encrypt and then switch the production ingress to `websecure` with a real TLS secret.

## Heavy import consideration

For large concurrent Excel imports:

- Increase Odoo `workers` based on CPU cores.
- Keep resource requests/limits conservative and monitor before raising.
- Consider moving long import processing to queued/background jobs to avoid request timeouts.
- Ensure PostgreSQL backups are automated before production go-live.
