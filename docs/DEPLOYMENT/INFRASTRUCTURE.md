# Infrastructure Guide — DigitalOcean

**Last updated**: June 2026

This document covers server sizing, managed services, storage, and the upgrade path for deploying on DigitalOcean. For the step-by-step first-deploy procedure see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

---

## Table of Contents

1. [Production Stack Summary](#1-production-stack-summary)
2. [Droplet Sizing](#2-droplet-sizing)
3. [Managed Database](#3-managed-database)
4. [Managed Redis](#4-managed-redis)
5. [Object Storage (Spaces)](#5-object-storage-spaces)
6. [Networking](#6-networking)
7. [Cost Summary by Stage](#7-cost-summary-by-stage)
8. [Upgrade Triggers](#8-upgrade-triggers)
9. [Backup Policy](#9-backup-policy)

---

## 1. Production Stack Summary

Every component the platform runs in production:

| Service | What it does | Where it runs |
|---|---|---|
| nginx | SSL termination, rate limiting, static files, WS proxy | Droplet |
| Daphne (ASGI) | Django HTTP + WebSocket server | Droplet |
| Celery worker | Background tasks (email, SLA, notifications) | Droplet |
| Celery beat | Scheduled tasks (overdue detection, stuck orders) | Droplet |
| PostgreSQL 15 | Primary database | Managed DB node |
| Redis 7 | Celery broker + channel layer + cache | Droplet (or Managed) |
| Static files | CSS/JS/fonts after `collectstatic` | DigitalOcean Spaces |
| Media files | User uploads, order attachments | DigitalOcean Spaces |
| Certbot | SSL certificate renewal | Droplet (cron container) |

---

## 2. Droplet Sizing

### Recommended: CPU-Optimized 4 vCPU / 8 GB — ~$84/mo

| Droplet type | vCPU | RAM | Disk | $/mo | Verdict |
|---|---|---|---|---|---|
| Basic 2 vCPU / 4 GB | 2 | 4 GB | 80 GB SSD | ~$24 | **Too tight.** Celery (4 workers) + Daphne + Redis compete for CPU at even moderate load. DB queries slow under memory pressure. |
| Basic 4 vCPU / 8 GB | 4 | 8 GB | 160 GB SSD | ~$48 | Functional at launch. Standard SSD limits DB I/O throughput under write-heavy workloads (order creation, file uploads). |
| **CPU-Optimized 4 vCPU / 8 GB** | **4** | **8 GB** | **25 GB NVMe** | **~$84** | **Recommended launch floor.** Faster cores matter for Daphne handling concurrent HTTP+WebSocket and for Celery running pricing calculations, SLA sweeps, and email batches simultaneously. NVMe meaningfully reduces DB I/O latency. |
| General Purpose 4 vCPU / 16 GB | 4 | 16 GB | 60 GB NVMe | ~$126 | Right tier when serving 3+ active tenant websites or when Celery queue depth is consistently non-zero. |
| General Purpose 8 vCPU / 32 GB | 8 | 32 GB | 130 GB NVMe | ~$252 | Scale-out tier — at this point horizontal scaling (multiple web containers) is usually better than vertical. |

### Why CPU-Optimized over Basic at the same RAM

Daphne is an async ASGI server — it serves HTTP and WebSocket connections in a single process using Python asyncio. Concurrent WebSocket connections (live order notifications) and simultaneous REST calls to the pricing or order APIs all compete for CPU cycles, not just memory. The CPU-Optimized tier provides dedicated vCPUs (vs shared on Basic), which prevents noisy-neighbour slowdowns when multiple tenants are active simultaneously.

### Single-page apps ship from Spaces, not the Droplet

The Vue 3 SPA is built to static files and hosted on DigitalOcean Spaces (CDN). Only API and WebSocket traffic hits the Droplet. This keeps the Droplet CPU budget available for Django, Celery, and Daphne — not for serving HTML/JS/CSS.

---

## 3. Managed Database

**Use DigitalOcean Managed PostgreSQL from day one.**

| Option | $/mo | Notes |
|---|---|---|
| Managed PostgreSQL Basic (1 vCPU / 1 GB) | ~$15 | Handles initial load easily. Automated backups, failover, monitoring included. |
| Managed PostgreSQL Standard (2 vCPU / 2 GB) | ~$38 | Upgrade to this when DB query times exceed 50ms on average or when you have 5+ active tenants. |

**Why Managed, not a container on the Droplet:**

- Automated daily backups with point-in-time recovery (up to 7 days). Manual `pg_dump` is not a substitute for this.
- Automated minor version upgrades and security patches.
- DigitalOcean monitors for disk space, connections, and query performance — you get alerts before things break.
- Connection pooling via PgBouncer is available built-in.
- Migrating Postgres out of a Docker container later is painful. Start managed.

**Connection string format for `.env`:**

```bash
DATABASE_URL=postgres://doadmin:<password>@<managed-db-host>:25060/defaultdb?sslmode=require
```

DigitalOcean Managed Databases only accept TLS connections — `?sslmode=require` is mandatory.

---

## 4. Managed Redis

**Optional at launch. Strongly recommended when you have 2+ tenant websites.**

| Option | $/mo | Notes |
|---|---|---|
| Redis in Docker on Droplet | $0 extra | Fine for a single-tenant launch. Shares Droplet memory. If Redis crashes, Celery stops. |
| Managed Redis Basic (1 GB) | ~$15 | No ops. Redis is monitored, auto-restarted, and backed up. Celery/Channels reconnect automatically. |

The `docker-compose.prod.yml` includes Redis as a container. To switch to Managed Redis, replace the Redis service block with your Managed Redis connection string in `.env`:

```bash
REDIS_URL=rediss://default:<password>@<managed-redis-host>:25061/0
CELERY_BROKER_URL=rediss://default:<password>@<managed-redis-host>:25061/0
CHANNEL_REDIS_URL=rediss://default:<password>@<managed-redis-host>:25061/2
```

Note: Managed Redis uses `rediss://` (TLS) not `redis://`.

---

## 5. Object Storage (Spaces)

**DigitalOcean Spaces is the storage backend for all user-uploaded files and built frontend assets.**

### Setup

1. Create a Space in the same region as your Droplet (e.g. `fra1` or `nyc3`)
2. Enable CDN on the Space
3. Create an API key (Spaces access key + secret)
4. Set in `.env`:

```bash
USE_S3=True
AWS_ACCESS_KEY_ID=<spaces-key>
AWS_SECRET_ACCESS_KEY=<spaces-secret>
AWS_STORAGE_BUCKET_NAME=<space-name>
AWS_S3_ENDPOINT_URL=https://fra1.digitaloceanspaces.com
AWS_S3_REGION_NAME=fra1
AWS_S3_CUSTOM_DOMAIN=<space-name>.fra1.cdn.digitaloceanspaces.com
```

### What gets stored

| Type | Path prefix | Access |
|---|---|---|
| Django static files (`collectstatic`) | `static/` | Public |
| User-uploaded order attachments | `media/orders/` | Private (signed URLs) |
| Writer-uploaded deliverables | `media/deliverables/` | Private (signed URLs) |
| Profile images | `media/profiles/` | Public |

### Cost

Spaces: $5/mo for 250 GB storage + 1 TB transfer. Exceeding those limits is billed at $0.02/GB storage and $0.01/GB transfer. For a new platform this will be well within the base tier for the first 6–12 months.

---

## 6. Networking

### VPC (Virtual Private Cloud)

Place the Droplet and Managed Database in the same DigitalOcean VPC. This keeps database traffic on the private network (not the public internet) and removes the need for SSL within your own infrastructure (SSL is still required from the internet to nginx).

### Firewall rules (DigitalOcean Cloud Firewall)

Configure at the DigitalOcean control panel, not inside the Droplet:

| Inbound | Port | Source |
|---|---|---|
| HTTP | 80 | All IPv4/IPv6 (for Certbot ACME) |
| HTTPS | 443 | All IPv4/IPv6 |
| SSH | 22 | Your IP only (or VPN range) |

All other inbound ports blocked. Daphne (8000), PostgreSQL (5432), and Redis (6379) are not exposed to the internet — they communicate only within the VPC or within the Docker network.

### DNS

Point your domain's A record to the Droplet's IP before running Certbot. Use DigitalOcean's nameservers or your existing DNS provider.

For multi-tenant deployments with multiple client domains (e.g. `client.essaybrand.com`, `client.techwriters.io`), each domain needs its own A record pointing to the same Droplet IP. nginx serves the correct portal based on the `server_name` directive.

---

## 7. Cost Summary by Stage

### Launch — single website (~$104/mo)

| Component | $/mo |
|---|---|
| CPU-Optimized Droplet 4 vCPU / 8 GB | $84 |
| Managed PostgreSQL Basic | $15 |
| Spaces (250 GB) | $5 |
| **Total** | **$104** |

Redis runs in Docker on the Droplet at this stage. No extra cost.

### Growth — 3–5 websites (~$163/mo)

| Component | $/mo |
|---|---|
| General Purpose Droplet 4 vCPU / 16 GB | $126 |
| Managed PostgreSQL Standard | $38 |
| Managed Redis Basic | $15 |
| Spaces | $5 |
| **Total** | **$184** |

### Scale — 5+ websites or high traffic (~$370+/mo)

At this point, split Celery workers onto a dedicated second Droplet and use load balancing for the web tier. DigitalOcean Load Balancer is ~$12/mo and supports sticky sessions for WebSocket.

---

## 8. Upgrade Triggers

Monitor these signals in DigitalOcean's built-in Droplet metrics:

| Signal | Threshold | Action |
|---|---|---|
| CPU utilisation | > 70% sustained (5+ min) | Upgrade Droplet or scale web containers horizontally |
| RAM usage | > 80% | Upgrade Droplet |
| Celery queue depth | > 5 tasks pending consistently | Add a second Celery worker container or increase `--concurrency` |
| DB average query time | > 50ms | Upgrade Managed DB tier or add indexes |
| Redis memory usage | > 70% of instance RAM | Upgrade Managed Redis |
| Disk usage | > 80% | Expand Droplet volume or move media to Spaces exclusively |

### Check Celery queue depth

```bash
docker compose exec web python manage.py celery inspect reserved
# or
docker compose exec redis redis-cli -a $REDIS_PASSWORD llen celery
```

---

## 9. Backup Policy

### Database (Managed PostgreSQL)

DigitalOcean takes daily automated backups with 7-day retention. Enable weekly automated snapshots in the control panel for 30-day coverage.

Manual backup before any risky migration:

```bash
# From outside the Droplet
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql
```

### Media files (Spaces)

Enable versioning on the Space for media files. This protects against accidental deletion but not against overwriting — use a lifecycle policy to expire old versions after 30 days to control costs.

### Droplet snapshot

Take a Droplet snapshot before every production deployment. DigitalOcean charges $0.06/GB/mo for snapshots. A 25 GB NVMe Droplet snapshot costs ~$1.50/mo. This is the fastest recovery path if a deploy breaks the server.

```bash
# Via DigitalOcean API or control panel — do this before each deploy
doctl compute droplet-action snapshot <droplet-id> --snapshot-name "pre-deploy-$(date +%Y%m%d)"
```
