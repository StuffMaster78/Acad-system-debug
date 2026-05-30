# Writing System Backend

Backend-first repository for the Writing System platform.

The legacy frontend, `client_frontend`, `blog_pages_management`, and
`service_pages_management` code has been removed while the next product
frontend is designed from scratch. This repository should now be treated as
the backend/API source of truth, with frontend code living in a separate
package or repository when that work begins.

## Current Scope

- Django and Django REST Framework API backend
- PostgreSQL, Redis, Celery, and Celery Beat services
- Multi-tenant website, account, order, payment, file, notification, support,
  discount, wallet, review, and governance domains
- OpenAPI schema generation through drf-spectacular
- Docker Compose and Makefile commands for backend development

## Packaging Direction

The project is being prepared for a split architecture:

- `writing-backend`: this Django API, domain logic, migrations, tasks, and
  OpenAPI contract
- `writing-frontend`: a fresh frontend for all portals and dashboards, built
  against the OpenAPI contract
- `writing-infra`: deployment, observability, runtime configuration, and
  environment orchestration
- `writing-docs`: optional living documentation, product specs, and API
  integration notes

Until the split happens, this repository should stay backend-only. Do not add
new frontend application code, generated API clients, or dashboard builds here.

See [docs/PACKAGING_STRATEGY.md](docs/PACKAGING_STRATEGY.md) for the working
plan.

## Backend Setup

### Local Python

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker Compose

```bash
docker-compose up -d
docker-compose logs -f web
```

The API runs on `http://localhost:8000` by default.

## Useful Commands

```bash
make install-backend
make dev-backend
make check-backend
make schema
make test-backend
make lint-backend
make clean
```

Direct verification commands:

```bash
cd backend
.venv/bin/python manage.py check --settings=writing_system.settings_test
.venv/bin/python manage.py spectacular --file /tmp/writing-system-schema.yml --settings=writing_system.settings_test
```

## API Documentation

When the backend is running:

- Swagger UI: `http://localhost:8000/api/v1/docs/swagger/`
- ReDoc: `http://localhost:8000/api/v1/docs/redoc/`
- OpenAPI schema: `http://localhost:8000/api/v1/schema/`

## Repository Layout

```text
writing_project/
├── backend/              # Django backend and domain modules
├── docs/                 # Living docs and migration notes
├── docker-compose.yml    # Local backend services
├── Makefile              # Backend development commands
└── README.md
```

## Current Readiness Notes

The backend passes Django system checks with the test settings. OpenAPI schema
generation completes, but the schema still reports many quality warnings and
errors from serializers/views. Those schema issues are the next major backend
readiness pass before the new frontend should depend on generated API types.


---

## Documentation

Full docs at /docs/:
- docs/USER_GUIDES/ - Role guides (client, writer, editor, support, admin, superadmin)
- docs/DEPLOYMENT/DEPLOYMENT_GUIDE.md - Docker, nginx, SSL, GitHub Actions
- docs/API/API_DOCUMENTATION.md - REST API reference
- backend/GETTING_STARTED.md - Local dev setup
- .github/SECRETS_SETUP.md - GitHub Actions secrets

## Quick Start

```bash
cp backend/.env.example backend/.env
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_templates
```

Frontend:
```bash
cd frontend && pnpm install && pnpm dev
```

Wagtail CMS admin: http://localhost:8000/cms-admin/

**Last Updated**: May 2026
