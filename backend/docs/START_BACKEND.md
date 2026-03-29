# Starting the Backend Server

## Quick Start

```bash
cd writing_system_backend
docker-compose up -d web
```

Wait about 10 seconds for the server to start, then verify:

```bash
curl http://localhost:8000/api/v1/
```

## Check Status

```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs web --tail 50

# Check if API is responding
curl http://localhost:8000/api/v1/
```

## Troubleshooting

### Container won't start

```bash
# View logs
docker-compose logs web

# Restart
docker-compose restart web

# Rebuild if needed
docker-compose up -d --build web
```

### Port 8000 already in use

```bash
# Find what's using port 8000
lsof -i :8000

# Or change port in docker-compose.yml
# Then update API_BASE_URL in frontend
```

### Container starts but API doesn't respond

1. Check logs: `docker-compose logs web`
2. Check if migrations are needed: `docker-compose exec web python manage.py migrate`
3. Check if static files are collected: `docker-compose exec web python manage.py collectstatic --noinput`

## Running Integration Tests

After backend is running:

```bash
# Option 1: Run from host (recommended)
./run_integration_tests.sh

# Option 2: Run inside container (needs network setup)
docker-compose exec web python test_frontend_backend_integration.py
```

## Environment Variables

Make sure these are set if needed:
- `DEBUG=True` (for development)
- `DATABASE_URL` (if using external database)
- `REDIS_URL` (if using Redis)

