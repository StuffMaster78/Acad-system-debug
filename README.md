# Writing System

Full-stack monorepo for a multi-tenant writing services platform.

**Backend:** Django 5.2 · DRF · Wagtail · Celery · Postgres · Redis  
**Frontend:** Vue 3 · Vite · Pinia · TypeScript · Tailwind  
**Portals:** Client domains · Writer domain · Staff domain (separate per surface)

---

## Repository Layout

```text
writing_project/
├── backend/              # Django API, domain apps, migrations, Celery tasks
├── frontend/             # Vue 3 SPA — all role portals in one build
├── nginx/                # Reverse proxy config (HTTP → HTTPS, static, SSE)
├── docs/                 # Architecture notes, API reference, deployment guide
├── docker-compose.yml    # Local dev services (Postgres, Redis, Django, Celery)
├── docker-compose.prod.yml  # Production overlay (nginx, Certbot, S3, Sentry)
├── Makefile              # Dev commands for backend and frontend
└── .github/workflows/    # CI (backend + frontend), deploy, PR hygiene
```

---

## Quick Start

### 1. Environment

```bash
cp backend/.env.example backend/.env
# Fill in SECRET_KEY, DB credentials, and REDIS_URL at minimum
```

### 2. Backend (Docker)

```bash
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

API: `http://localhost:8000`  
Wagtail CMS: `http://localhost:8000/cms-admin/`  
Swagger UI: `http://localhost:8000/api/v1/docs/swagger/`

### 3. Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Dev server: `http://localhost:5174`  
Set `VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env.local` to proxy API calls.

### 4. Backend (local Python, no Docker)

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Makefile Commands

```bash
# Backend
make check-backend       # Django system check (test settings)
make test-backend        # pytest
make lint-backend        # flake8 + black + isort check
make lint-fix-backend    # black + isort auto-fix
make schema              # Generate OpenAPI schema → /tmp/writing-system-schema.yml
make migrate             # Run migrations

# Frontend
make install-frontend    # pnpm install
make dev-frontend        # pnpm dev (hot-reload dev server)
make build-frontend      # pnpm build
make typecheck           # vue-tsc --noEmit
make test-frontend       # vitest

# Combined
make install             # install backend + frontend deps
make check               # backend system check + frontend typecheck
make test                # backend pytest + frontend vitest
```

---

## Portal Architecture

The platform serves three separate surfaces, each on its own domain:

| Domain type | Surface | Roles |
|---|---|---|
| Client domains (e.g. `essaybrand.com`) | `client` | client |
| Writer domain (e.g. `writers.platform.com`) | `writer` | writer |
| Staff domain (e.g. `staff.platform.com`) | `staff` | superadmin, admin, editor, support |

At boot, the frontend calls `GET /api/v1/portal-context/` (resolved from the request host by `PortalTenantResolverMiddleware`) and receives the surface type, website branding, payment disclosure config, and allowed roles. The router then enforces surface boundaries — a client domain cannot reach writer or staff routes.

---

## Payment Disclosure

All client payment surfaces (new order, order payments tab, wallet top-up, express special order) show the payment processor name and card statement descriptor before the pay button, and again on confirmation. The disclosure copy is configured per website on `WebsiteBranding.payment_processor_name` / `payment_statement_descriptor` and flows through the portal context endpoint automatically.

---

## CI

| Workflow | Trigger | Covers |
|---|---|---|
| `ci.yml` | push/PR to main, develop, feature/\* | Django check · pytest · schema generation |
| `frontend-ci.yml` | push/PR touching `frontend/` | vue-tsc · vite build · vitest |
| `deploy-production.yml` | push `v*.*.*` tag or manual | CI gate → SSH deploy to prod server |
| `pr-checks.yml` | every PR | semantic title · merge conflicts · large files · secret scan |

Runtime: Python 3.12 · Node 20 · pnpm (version from `package.json`)

---

## API Documentation

- Swagger UI: `http://localhost:8000/api/v1/docs/swagger/`
- ReDoc: `http://localhost:8000/api/v1/docs/redoc/`
- Portal context: `GET /api/v1/portal-context/` (public)

Full docs: [docs/](docs/)
