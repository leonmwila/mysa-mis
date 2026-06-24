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

## 3) Production VM

Deploy production overlay:

```bash
kubectl apply -k k8s/overlays/production
```

Before deploying, update:

- `k8s/overlays/production/postgres-secret-patch.yaml`
- `k8s/overlays/production/odoo-config-patch.yaml`
- `k8s/overlays/production/ingress-patch.yaml` (host and TLS secret)
- `k8s/overlays/production/kustomization.yaml` image owner

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
- Staging/Production on K3s: Traefik is a good default.
- For TLS automation, add cert-manager with Let’s Encrypt and switch TLS secrets to cert-manager managed certificates.

## Heavy import consideration

For large concurrent Excel imports:

- Increase Odoo `workers` based on CPU cores.
- Keep resource requests/limits conservative and monitor before raising.
- Consider moving long import processing to queued/background jobs to avoid request timeouts.
- Ensure PostgreSQL backups are automated before production go-live.
