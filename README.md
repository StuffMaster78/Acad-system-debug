# Writing System Platform

> A multi-tenant writing services platform. Clients place academic and professional writing orders, writers bid and deliver, staff manage the full lifecycle — all across separate branded domains.

[![Backend CI](https://img.shields.io/badge/backend-Django%205.2-092E20?logo=django)](backend/)
[![Frontend](https://img.shields.io/badge/frontend-Vue%203%20%2B%20TypeScript-41B883?logo=vue.js)](frontend/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Docker](https://img.shields.io/badge/dev-Docker%20Compose-2496ED?logo=docker)](docker-compose.yml)

---

## What it does

| Surface | Who | What they do |
|---------|-----|-------------|
| **Client portal** | Clients | Place orders, track progress, chat with support, pay via wallet or card |
| **Writer portal** | Writers | Browse the pool, bid/take orders, submit deliveries, track earnings |
| **Staff portal** | Admin · Editor · Support · Superadmin | Manage orders, run QA, handle disputes, configure platform |

Each surface runs on its **own domain** and is isolated by the portal context system — a client on `essaybrand.com` never sees the writer or staff interface.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend API | Django 5.2 · Django REST Framework · Celery · Django Channels (WebSocket) |
| CMS | Wagtail 7 (tenant-scoped pages, SEO, sitemap) |
| Database | PostgreSQL 15 |
| Cache / Broker / Channels | Redis 7 (DB 0: cache/broker · DB 2: comms · DB 3: channel layer) |
| Frontend | Vue 3 · Vite · Pinia · TypeScript · Tailwind CSS |
| Auth | JWT (SimpleJWT) · MFA-ready · device fingerprinting · session limits |
| Payments | Stripe (webhook-driven) · platform wallet · per-tenant billing |
| Storage | S3 / DigitalOcean Spaces (production) · local (dev) |
| Server | Daphne (ASGI — HTTP + WebSocket) |
| Deployment | Docker Compose (dev) · nginx + Certbot + Daphne (prod) |

---

## Quick Start

### Prerequisites

- Docker Desktop 4.x+
- Node 20+ and `npm`

### 1. Clone and configure

```bash
git clone <repo-url> writing_project
cd writing_project
cp backend/.env.example backend/.env
# Minimum required vars: SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD
```

### 2. Start the stack

```bash
docker compose up -d
```

Services started: `web` (Django), `celery`, `beat`, `db` (Postgres), `redis`.

Wait ~15 s for the health checks to pass, then:

```bash
# Apply migrations and seed demo data
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_orders --count 50
docker compose exec web python manage.py seed_special_orders
docker compose exec web python manage.py seed_announcements
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

App: **http://localhost:5173**  
API: **http://localhost:8000**  
Swagger: **http://localhost:8000/api/v1/docs/swagger/**  
Wagtail CMS: **http://localhost:8000/cms-admin/**

---

## Demo Accounts

| Role | Email | Password | Access |
|------|-------|----------|--------|
| Superadmin | `admin.demo@example.com` | `AdminDemo123!` | Full platform |
| Client | `client.demo@example.com` | `ClientDemo123!` | Client portal |
| Writer | `writer1.demo@example.com` | `WriterDemo123!` | Writer portal |

> **Express preview** — on the login page click any role button in the "Preview workspace" panel to instantly browse that role's dashboard with mock data. No password required.

---

## Repository Layout

```text
writing_project/
├── backend/
│   ├── writing_system/        # Django settings, URLs, Celery config
│   ├── accounts/              # Users, roles, portal definitions
│   ├── authentication/        # JWT login, MFA, impersonation, device fingerprinting
│   ├── orders/                # Order lifecycle, staffing, assignments, QA
│   ├── special_orders/        # Quoted / fixed-price / sensitive orders
│   ├── class_management/      # Long-running class portals and coursework
│   ├── payments_processor/    # Stripe integration, webhooks, reconciliation
│   ├── wallets/               # Client and writer wallet + ledger
│   ├── communications/        # Message threads, SSE, moderation
│   ├── notifications_system/  # In-app + email notifications, digest
│   ├── websites/              # Multi-tenant website model + branding
│   ├── cms_core/              # Wagtail CMS (tenant-scoped)
│   ├── loyalty_management/    # Points, tiers, redemption
│   ├── writer_management/     # Writer profiles, levels, badges, discipline
│   ├── analytics/             # Revenue, orders, client, and writer charts
│   └── ...                    # 40+ additional domain apps
├── frontend/
│   ├── src/
│   │   ├── layouts/           # DashboardLayout (shared by all roles)
│   │   ├── views/             # Per-role views (admin/, client/, writer/, etc.)
│   │   ├── stores/            # Pinia stores (one per domain)
│   │   ├── api/               # Typed axios wrappers
│   │   ├── components/        # Shared UI components
│   │   ├── composables/       # useNotifications, useDashboardData, etc.
│   │   ├── config/            # Navigation, dashboard definitions
│   │   └── router/            # Surface-aware routing + role guards
│   └── ...
├── docker-compose.yml         # Dev stack
├── docker-compose.prod.yml    # Production overlay (nginx, Certbot, S3)
└── Makefile                   # Dev commands
```

---

## Architecture & Diagrams

Full architecture diagrams (system overview, order lifecycle state machine, notification pipeline, compensation flow, authentication sequence, and more) are in **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

---

## Portal Architecture

```
Request Host           → PortalTenantResolverMiddleware → request.portal + request.website
                                                               │
Frontend boot          → GET /api/v1/portal-context/          │
                       ← { surface, website, branding,        │
                            payment_disclosure,               │
                            allowed_roles }                   │
                                                               │
Router beforeEach      → enforce surface boundaries           │
                          (client domain ≠ staff routes)      │
```

Three surfaces run independently:

| Domain | Surface | Roles |
|--------|---------|-------|
| `yourplatform.com` | `staff` | superadmin, admin, editor, support |
| `writers.yourplatform.com` | `writer` | writer |
| `client-brand.com` (any number) | `client` | client |

---

## Role Capabilities

| Role | Dashboards | Key actions |
|------|-----------|-------------|
| **Superadmin** | Platform command · Tenant health · Cross-tenant finance | Manage tenants, impersonate users, configure platform |
| **Admin** | Operations center · Order ops | Assign writers, approve delivery, manage disputes, send mass emails |
| **Editor** | QA desk · Workload | Review submissions, return drafts, approve delivery |
| **Support** | Rescue queue · SLA board | Handle tickets, escalations, refunds, client rescue |
| **Writer** | My workspace · Earnings | Browse pool, bid/take orders, submit work, track payouts |
| **Client** | Portal home · Orders | Place orders, pay, revise, message, view loyalty points |

---

## Key Features

### Orders
- Full lifecycle: created → staffing → assigned → in-progress → submitted → QA → approved
- Preferred writer routing, re-assignment, holds, disputes
- Revision windows, QA scoring, delivery guard (blocks download until paid)

### Special Orders
- Quoted, fixed-price, sensitive, and milestone-based workflows
- Per-milestone delivery and approval
- Two-factor sensitive access for vault files

### Classes
- Long-running class portals with task, milestone, and assignment management
- Per-task submission forms for client and writer
- Writer compensation tracking

### Payments
- Stripe webhooks + platform wallet + split payments
- Per-tenant payment disclosure (intermediary merchant model)
- Ledger double-entry bookkeeping for all wallet movements

### Writer Management
- Level-based intake limits (`max_active_orders`, `max_manual_takes`)
- Badges (manual admin award or auto-award via rule codes)
- Discipline: warnings, strikes, suspension, blacklist, probation

### Impersonation
- Staff can impersonate any user with full audit trail
- Amber banner shown throughout the session
- One-click "End impersonation" restores original session

---

## Celery Tasks

Background tasks are registered via `CELERY_IMPORTS` in Django settings. Workers process:
- Notification delivery (email + in-app)
- Badge auto-award evaluation
- Order monitoring (overdue, SLA breach)
- Wallet hold expiry
- Payment reconciliation

Beat schedule is stored in `django-celery-beat` (database-backed, editable in staff admin).

---

## API Documentation

| URL | Description |
|-----|-------------|
| `/api/v1/portal-context/` | Public boot endpoint — surface, branding, payment disclosure |
| `/api/v1/auth/login/` | JWT login |
| `/api/v1/auth/impersonation/` | Start / end / status |
| `/api/v1/orders/` | Order CRUD + lifecycle actions |
| `/api/v1/special-orders/` | Special order management |
| `/api/v1/class-management/classes/` | Class management |
| `/api/v1/analytics/charts/` | Revenue, orders, clients (staff-only) |
| `/api/v1/writer-management/badges/` | Badge definitions + award |
| `/api/v1/docs/swagger/` | Interactive Swagger UI |
| `/api/v1/docs/redoc/` | ReDoc reference |

---

## Development

### Makefile commands

```bash
make migrate           # Run Django migrations
make check-backend     # Django system check
make test-backend      # pytest
make seed              # Seed demo data (orders, badges, announcements)

make dev-frontend      # npm run dev
make build-frontend    # npm run build
make typecheck         # vue-tsc --noEmit
make test-frontend     # vitest
```

### Environment variables

Key variables in `backend/.env`:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret key |
| `POSTGRES_DB_NAME` | Database name |
| `POSTGRES_PASSWORD` | DB password |
| `REDIS_URL` | Redis connection string |
| `CELERY_BROKER_URL` | Celery broker (usually same as REDIS_URL) |
| `STRIPE_SECRET_KEY` | Stripe API key (optional in dev) |
| `USE_S3` | `True` to use S3 storage (default `False`) |
| `SENTRY_DSN` | Error tracking (optional) |

### Running tests

```bash
# Backend
docker compose exec web pytest tests/ -q

# Frontend
cd frontend && npm run test
```

---

## Production Deployment

```bash
# Tag a release
git tag v1.0.0 && git push origin v1.0.0
```

The `deploy-production.yml` GitHub Action runs CI then deploys via SSH. The `docker-compose.prod.yml` overlay adds:
- `nginx` — reverse proxy, SSL termination, static file serving
- `certbot` — automatic Let's Encrypt certificate renewal
- S3 media storage
- Sentry error tracking

---

## Status

| Area | Status |
|------|--------|
| Core order lifecycle | ✅ Production-ready |
| Payments + wallet | ✅ Production-ready |
| Special orders | ✅ Production-ready |
| Classes | ✅ Production-ready |
| Notifications (in-app + email + WebSocket) | ✅ Production-ready |
| Analytics + chart views | ✅ Production-ready |
| CMS / SEO / publishing | ✅ Production-ready |
| Multi-domain portal (surface routing) | ✅ Production-ready |
| Writer pay + compensation events | ✅ Production-ready |
| Writer vetting + quiz gate | ✅ Production-ready |
| Dispute resolution workflow | ✅ Production-ready |
| Coupon / discount checkout | ✅ Production-ready |
| Real-time WebSocket notifications | ✅ Production-ready (requires Daphne) |
| Operations Command Center | ✅ Production-ready |
| Writer public profiles | ✅ Production-ready |
| Stripe live keys | ⚙️ Set `STRIPE_SECRET_KEY` etc. in `.env` before go-live |
| DNS / nginx domain | ⚙️ Replace `YOUR_DOMAIN` in `nginx/nginx.conf` |
| SSL certificate | ⚙️ Run Certbot after DNS is pointed |

---

## License

MIT — see [LICENSE](LICENSE).
