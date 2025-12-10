# Odoo Docker Setup

## Prerequisites
- Docker Desktop installed and running
- Docker Compose

## Quick Start

### 1. Start Odoo and PostgreSQL
```bash
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

### Restart Odoo (after code changes)
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
- `custom_addons/` - Your custom Odoo modules (mounted to container)
- `odoo-docker.conf` - Odoo configuration for Docker
- `docker-compose.yml` - Docker services configuration

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
