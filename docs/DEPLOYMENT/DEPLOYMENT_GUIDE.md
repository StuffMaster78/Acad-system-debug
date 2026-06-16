# Deployment Guide

**Last updated:** June 2026

---

## Overview

Production stack: **nginx → Daphne (ASGI)** serving both HTTP and WebSocket, backed by PostgreSQL 15, Redis 7, and Celery workers. Static/media files served from S3-compatible storage.

```
Internet → nginx (SSL, rate-limit) → Daphne:8000 (HTTP + WebSocket)
                                    → Celery worker (async tasks)
                                    → Celery beat (scheduled tasks)
```

---

## Pre-Deploy Checklist

- [ ] All tests passing (`pytest` backend, `vue-tsc --noEmit` frontend)
- [ ] `.env` populated (see below)
- [ ] DNS A records for all domains point to the server IP
- [ ] Stripe live keys set
- [ ] `DEBUG=False` confirmed

---

## Environment Variables (`.env`)

Copy `backend/env.template` as your starting point. Key values:

```bash
# Core
SECRET_KEY=<long random string>
DEBUG=False
ALLOWED_HOSTS=writerscreek.com,www.writerscreek.com,app.writerscreek.com,admin.writerscreek.com,gradecrest.com
DJANGO_SETTINGS_MODULE=writing_system.settings

# Database
POSTGRES_DB_NAME=writing_system_db
POSTGRES_USER_NAME=postgres
POSTGRES_PASSWORD=<strong password>

# Redis (single host, different DBs)
REDIS_PASSWORD=<strong password>
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0
COMMUNICATIONS_REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/2
CHANNEL_REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/3

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Storage (S3 / DigitalOcean Spaces)
USE_S3=True
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=...
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_S3_REGION_NAME=nyc3

# Email
SENDGRID_API_KEY=SG....
DEFAULT_FROM_EMAIL=noreply@writerscreek.com

# Security — CORS and CSRF must include every origin that POSTs to Django
CORS_ALLOWED_ORIGINS=https://app.writerscreek.com,https://writerscreek.com,https://admin.writerscreek.com,https://gradecrest.com
CSRF_TRUSTED_ORIGINS=https://app.writerscreek.com,https://writerscreek.com,https://admin.writerscreek.com,https://gradecrest.com

# Shared session cookie — enables single-login at writerscreek.com/login
# that routes writers → app.writerscreek.com and staff → admin.writerscreek.com
SESSION_COOKIE_DOMAIN=.writerscreek.com
CSRF_COOKIE_DOMAIN=.writerscreek.com

FIELD_ENCRYPTION_KEY=<fernet key>
TOKEN_ENCRYPTION_KEY=<fernet key>

# Optional
SENTRY_DSN=https://...@sentry.io/...
WAGTAILADMIN_BASE_URL=https://admin.writerscreek.com

# Nuxt marketing sites
NUXT_PUBLIC_WC_API_BASE=https://writerscreek.com
NUXT_PUBLIC_WC_APP_URL=https://app.writerscreek.com
NUXT_PUBLIC_WC_STAFF_URL=https://admin.writerscreek.com
NUXT_PUBLIC_API_BASE=https://gradecrest.com
NUXT_PUBLIC_APP_URL=https://app.gradecrest.com
```

---

## First Deploy

```bash
# 1. Start stack (HTTP only first — Certbot needs port 80 for ACME challenge)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 2. Issue SSL certificates (one command per domain group)
#    writerscreek.com marketing site + www redirect
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d writerscreek.com -d www.writerscreek.com \
  --email admin@writerscreek.com --agree-tos --non-interactive

#    app.writerscreek.com — writer portal
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d app.writerscreek.com \
  --email admin@writerscreek.com --agree-tos --non-interactive

#    admin.writerscreek.com — staff portal
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d admin.writerscreek.com \
  --email admin@writerscreek.com --agree-tos --non-interactive

#    gradecrest.com — client marketing site
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d gradecrest.com -d www.gradecrest.com \
  --email admin@writerscreek.com --agree-tos --non-interactive

# 3. Restart nginx to pick up all certs
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx

# 4. Run migrations and seed data
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec web python manage.py seed_dev_data

# 5. Backfill compensation events (if migrating from an older environment)
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec web \
  python manage.py backfill_compensation_events --dry-run
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec web \
  python manage.py backfill_compensation_events
```

---

## WebSocket Support

The server uses **Daphne** (ASGI), not Gunicorn (WSGI). This is required for WebSocket notifications.

nginx is already configured to proxy `/ws/` routes:

```nginx
location /ws/ {
    proxy_pass http://django;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
}
```

The Content-Security-Policy header allows `wss:` in `connect-src` for secure WebSocket connections.

---

## Scaling

Daphne runs as a single async process by default. For high traffic, scale horizontally:

```bash
# Run 3 web replicas
docker compose -f docker-compose.prod.yml up -d --scale web=3
```

The Redis channel layer handles WebSocket group broadcasts across all replicas automatically.

---

## SSL Renewal

Certbot auto-renews via the cron container in `docker-compose.prod.yml`. Manual renewal:

```bash
docker compose -f docker-compose.prod.yml run --rm certbot renew
docker compose -f docker-compose.prod.yml restart nginx
```

---

## GitHub Secrets (CI/CD)

| Secret | Value |
|--------|-------|
| `PROD_SSH_HOST` | Server IP or hostname |
| `PROD_SSH_USER` | Deploy user |
| `PROD_SSH_KEY` | Private SSH key |
| `PROD_DEPLOY_PATH` | e.g. `/opt/writing-system` |
| `PROD_ENV_FILE` | Full contents of production `.env` |
| `PROD_DOMAIN` | (variable, not secret) `yourdomain.com` |

---

## Monitoring

- **Uptime Kuma**: `https://admin.writerscreek.com/status/` — restricted to trusted IPs in nginx config
- **Sentry**: set `SENTRY_DSN` in `.env` for error tracking
- **Health endpoint**: `GET /health/live/` — returns `{"status": "ok"}` (used by Docker healthcheck)

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| WebSocket 404 | Gunicorn (WSGI) still running | Ensure Dockerfile CMD uses Daphne |
| Celery/beat unhealthy | HTTP healthcheck on non-HTTP container | Override healthcheck (already done in compose) |
| `NoOpenWindowError` | No open PaymentWindow for a website | Run `manage.py manage_windows open --website-id=N` |
| Notifications not sending | Celery not running or SENDGRID_API_KEY missing | Check worker logs; set `SENDGRID_API_KEY` |
| 502 from nginx | Daphne not started | Check `docker compose logs web` |
| Static files 404 | `collectstatic` not run | `docker compose exec web python manage.py collectstatic` |
