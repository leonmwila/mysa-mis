# Kubernetes Deployment Setup (Minikube → Staging → Production)

## Overview

This repository now includes a complete Kubernetes deployment setup for Odoo (v19) with PostgreSQL. It supports three environments via Kustomize overlays:

1. **Local** (Minikube): For local development and testing.
2. **Staging** (K3s on VM): For pre-production validation.
3. **Production** (K3s on VM): For production with 2 Odoo replicas.

## Why Kubernetes?

For your use case (5 institutions importing thousands of records concurrently), Kubernetes provides:
- **Automatic scaling** via horizontal pod autoscaling.
- **Load balancing** across multiple Odoo replicas.
- **Self-healing** if a pod crashes.
- **Rolling updates** with zero downtime.
- **Resource isolation** for heavy import jobs.

## Quick Start

### Prerequisites

- Docker (for building the image)
- kubectl
- Minikube (for local), or K3s (for staging/production)
- kustomize (included with kubectl 1.14+)

### 1. Build Docker Image

```bash
# Local build (for Minikube)
docker build -t mysa-mis-odoo:local .

# Or push to GitHub Container Registry (GHCR)
docker build -t ghcr.io/your-username/mysa-mis:latest .
docker push ghcr.io/your-username/mysa-mis:latest
```

### 2. Deploy to Minikube (Local)

```bash
# Start Minikube with 4 CPUs and 8GB RAM
minikube start --cpus=4 --memory=8192

# Enable NGINX ingress
minikube addons enable ingress

# Build image into Minikube's Docker
eval "$(minikube -p minikube docker-env)"
docker build -t mysa-mis-odoo:local .

# Deploy local overlay
kubectl apply -k k8s/overlays/local

# Add local hosts entry (Linux/Mac)
echo "$(minikube ip) mysa.local" | sudo tee -a /etc/hosts

# Forward port if ingress doesn't work
kubectl port-forward -n mysa-mis svc/odoo 8069:8069

# Access at http://mysa.local or http://localhost:8069
```

**Credentials (local):** admin / admin@123  
**DB Credentials (local):** odoo / odoo

### 3. Deploy to Staging (K3s on VM)

**On the staging VM:**

```bash
# Install K3s (single-node or HA)
curl -sfL https://get.k3s.io | sh -

# Verify kubectl works
kubectl get nodes
```

**From your local machine:**

```bash
# Get kubeconfig from staging VM and save to ~/.kube/config-staging
scp user@staging-vm:/etc/rancher/k3s/k3s.yaml ~/.kube/config-staging
# Edit ~/.kube/config-staging and update server IP to staging VM's public IP

# Set KUBECONFIG
export KUBECONFIG=~/.kube/config-staging

# Before deploying, edit secrets and ingress
# vim k8s/overlays/staging/postgres-secret-patch.yaml  # Set DB password
# vim k8s/overlays/staging/odoo-config-patch.yaml      # Set admin password
# vim k8s/overlays/staging/ingress-patch.yaml          # Update hostname
# vim k8s/overlays/staging/kustomization.yaml          # Update image owner

# Deploy staging overlay
kubectl apply -k k8s/overlays/staging

# Check rollout
kubectl -n mysa-mis get pods
kubectl -n mysa-mis logs deployment/odoo -f
```

### 4. Deploy to Production (K3s on VM)

Similar to staging, but with production hardening (2 Odoo replicas, 6 workers, higher resource limits).

```bash
# Export production kubeconfig
export KUBECONFIG=~/.kube/config-production

# Before deploying, edit all secrets and configs for production
# vim k8s/overlays/production/postgres-secret-patch.yaml
# vim k8s/overlays/production/odoo-config-patch.yaml
# vim k8s/overlays/production/ingress-patch.yaml
# vim k8s/overlays/production/kustomization.yaml

# Deploy production overlay
kubectl apply -k k8s/overlays/production

# Check status
kubectl -n mysa-mis get pods
kubectl -n mysa-mis describe deployment odoo
```

## GitHub Actions CI/CD

Two workflows are included for automated builds and deployments:

### `.github/workflows/build-and-push-ghcr.yml`

Automatically builds and pushes the Docker image to GHCR when:
- You push to the `main` branch → `staging-latest` tag
- You create a git tag `v*` → `production-latest` tag
- Every commit gets a unique `sha-*` tag

**Setup:**
1. Ensure the image owner in `.github/workflows/build-and-push-ghcr.yml` matches your GitHub username.
2. The workflow uses `GITHUB_TOKEN` (automatic, no secrets needed for pushing).

### `.github/workflows/deploy-k8s.yml`

Manual workflow to deploy from GitHub to staging or production.

**Setup:**
1. Add GitHub repository secrets:
   - `KUBECONFIG_STAGING`: Full kubeconfig content for staging cluster
   - `KUBECONFIG_PRODUCTION`: Full kubeconfig content for production cluster
2. Use the **Actions** tab to trigger manually:
   - Select environment (staging or production)
   - Specify image tag (e.g., `sha-abc1234`)
3. Workflow validates rollout with `kubectl rollout status`

**Example:**
```bash
# After pushing code, the build workflow runs
# Once image is pushed (check GHCR), manually deploy via Actions UI:
# - Environment: staging
# - Image tag: sha-<commit-sha>
```

## Ingress & TLS

### Local (Minikube)
- Uses NGINX ingress (included in `minikube addons`)
- `http://mysa.local` (add to `/etc/hosts`)

### Staging/Production (K3s)
- Uses Traefik ingress (built into K3s)
- For TLS, either:
  - Use self-signed certs (testing)
  - Use cert-manager + Let's Encrypt (production)

**To set up cert-manager:**

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml

# Create Let's Encrypt issuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: traefik
EOF

# Update ingress annotation to use cert-manager
```

## Configuration for Heavy Imports

Since you're importing large Excel sheets from 5 institutions:

1. **Worker processes:** Increased in each overlay (local: 2, staging: 4, production: 6)
2. **Database connection limit:** 64 → 256 in production
3. **Resource limits:** Configured in production patch to allow scaling
4. **Long imports:** Consider implementing Odoo background jobs or async import processing

**Monitor during imports:**
```bash
# Watch Odoo logs
kubectl -n mysa-mis logs -f deployment/odoo --tail=50

# Check pod resource usage
kubectl -n mysa-mis top pods

# Check database connections
kubectl -n mysa-mis exec -it postgres-0 -- psql -U odoo -d postgres -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

## Persistent Storage

Both Odoo and PostgreSQL use `PersistentVolumeClaim` (PVC) for data:
- `postgres-data`: 30GB for database
- `odoo-data`: 30GB for Odoo filestore

**On local Minikube:** Stored in Minikube's VM  
**On K3s VMs:** Uses the default storage class (local-path provisioner)

To use external storage (NFS, cloud provider), update the `storageClassName` in the PVC manifests.

## Troubleshooting

### Odoo pod won't start
```bash
kubectl -n mysa-mis logs pod/<odoo-pod-name>
kubectl -n mysa-mis describe pod/<odoo-pod-name>
```

### Can't connect to database
```bash
# Test DB connection from Odoo pod
kubectl -n mysa-mis exec -it deployment/odoo -- \
  python3 -c "import psycopg2; psycopg2.connect('host=postgres user=odoo password=odoo')"
```

### Ingress not working
```bash
# Check ingress status
kubectl -n mysa-mis get ingress
kubectl -n mysa-mis describe ingress odoo

# For Minikube, verify IP
minikube ip
```

## Next Steps

1. **Test locally** with Minikube to validate the app runs correctly in containers.
2. **Set up GitHub Actions secrets** for staging/production kubeconfigs.
3. **Create staging VM** with K3s and configure DNS/ingress.
4. **Validate imports** in staging before promoting to production.
5. **Set up monitoring** (Prometheus, Grafana, or cloud provider dashboards).
6. **Automate backups** for PostgreSQL in production.

## Files Structure

```
k8s/
├── base/                          # Base Kubernetes resources
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── postgres-*.yaml
│   ├── odoo-*.yaml
│   └── ingress.yaml
├── overlays/
│   ├── local/                     # Minikube overrides
│   ├── staging/                   # Staging K3s overrides
│   └── production/                # Production K3s overrides
└── README.md                      # This file

.github/workflows/
├── build-and-push-ghcr.yml        # Automated Docker builds
└── deploy-k8s.yml                 # Manual Kubernetes deployments
```

## Questions?

Refer to:
- [Kustomize documentation](https://kustomize.io/)
- [Kubernetes documentation](https://kubernetes.io/docs/)
- [K3s documentation](https://docs.k3s.io/)
- [Traefik ingress documentation](https://doc.traefik.io/traefik/providers/kubernetes-crd/)
