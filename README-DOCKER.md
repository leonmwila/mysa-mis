# Odoo Docker Setup

## Prerequisites
- Docker Desktop installed and running
- Docker Compose

## Quick Start

### 1. Build and Start Odoo and PostgreSQL
```bash
# Build the custom Odoo image and start services
docker-compose up -d --build
```

**Note:** The first time you run this, Docker will build the custom Odoo image which includes your custom addons and dependencies. Subsequent starts will be faster.

### Alternative: Build separately
```bash
# Build the image first
docker-compose build

# Then start services
docker-compose up -d
```

### 2. View logs
```bash
docker-compose logs -f odoo
```

### 3. Access Odoo
Open your browser: http://localhost:8069

### 4. Create Database
- Master Password: `admin`
- Database Name: `mysa_mis`
- Email: your email
- Password: choose a password
- Language: your language
- Country: your country

## Common Commands

### Stop containers
```bash
docker-compose down
```

### Rebuild and Restart Odoo (after code changes)
```bash
# Rebuild the image with latest changes
docker-compose build odoo

# Restart the container
docker-compose restart odoo
```

### Restart Odoo (without rebuilding)
```bash
docker-compose restart odoo
```

### Update modules
```bash
docker-compose exec odoo odoo -u all -d mysa_mis --stop-after-init
docker-compose restart odoo
```

### Install a specific module
```bash
docker-compose exec odoo odoo -i module_name -d mysa_mis --stop-after-init
docker-compose restart odoo
```

### Access Odoo shell
```bash
docker-compose exec odoo odoo shell -d mysa_mis
```

### View PostgreSQL logs
```bash
docker-compose logs -f db
```

### Access PostgreSQL
```bash
docker-compose exec db psql -U odoo -d mysa_mis
```

### Clean everything (CAUTION: deletes all data)
```bash
docker-compose down -v
```

## Folder Structure
- `Dockerfile` - Custom Odoo image definition (includes custom addons and dependencies)
- `custom_addons/` - Your custom Odoo modules (copied into image)
- `odoo-docker.conf` - Odoo configuration for Docker
- `docker-compose.yml` - Docker services configuration
- `.dockerignore` - Files excluded from Docker build context
- `requirements.txt` - Python dependencies (installed in image)

## Troubleshooting

### Port already in use
If port 8069 is already in use, change it in `docker-compose.yml`:
```yaml
ports:
  - "8070:8069"  # Use port 8070 instead
```

### Reset database
```bash
docker-compose down
docker volume rm mysa_mis_odoo-db-data
docker-compose up -d
```

### View all running containers
```bash
docker ps
```

### Enter Odoo container
```bash
docker-compose exec odoo bash
```

### Rebuild image after dependency changes
If you update `requirements.txt` or modify the Dockerfile:
```bash
docker-compose build --no-cache odoo
docker-compose up -d
```

## Docker Image Details

The application uses a custom Dockerfile that:
- Bases on the official `odoo:19.0` image
- Copies your custom addons into the image
- Installs Python dependencies from `requirements.txt`
- Configures proper file permissions

This ensures your customizations are baked into the image for consistent deployments.
