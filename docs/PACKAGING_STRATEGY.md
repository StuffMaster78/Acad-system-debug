# Packaging Strategy

This is the working direction for making the project easier to follow, split,
and maintain.

## Decision

Do not physically split the repository yet.

First, stabilize the backend as the source of truth, finish cleaning legacy
frontend assumptions, and improve the OpenAPI contract. Once the new frontend
work starts, create a separate frontend package or repository that consumes the
backend contract instead of sharing application code with this repo.

## Target Shape

```text
writing-backend/
  Django API, domain modules, migrations, Celery tasks, OpenAPI schema

writing-frontend/
  Fresh portals and dashboards for clients, writers, editors, support,
  admins, and superadmins

writing-infra/
  Production deployment, environment orchestration, observability,
  reverse proxy, and cloud resources

writing-docs/ (optional)
  Product specs, API integration guides, design decisions, and runbooks
```

This can live under a GitHub organization later, similar to a clean
multi-repository product layout. The names above are placeholders; the
important boundary is backend, frontend, infrastructure, and docs.

## Current Repository Role

For now, `writing_project` is the backend/system repository.

It should contain:

- Django apps and migrations
- Backend tests
- Celery workers and scheduled tasks
- API schema generation
- Backend Docker development services
- Backend-facing docs and product notes

It should not contain:

- New frontend app source
- Generated frontend API clients
- Dashboard builds
- Node/Vite/Next project scaffolding
- Legacy frontend compatibility layers

## Backend Boundaries

Keep backend domains modular and explicit:

- `accounts`, `authentication`, `users`: identity and access
- `websites`: tenant/site context
- `orders`, `order_pricing_core`, `order_payments_management`: order and money
  workflows
- `files_management`: uploaded file lifecycle and metadata
- `communications`, `notifications_system`: messaging and notification
  surfaces
- `cms_core`, `cms_intelligence`: CMS infrastructure that still has an active
  backend reason to exist
- management apps: operational APIs for staff-facing domains

When a module only exists to serve a deleted frontend or old CMS surface, remove
it or fold the durable behavior into a real backend domain.

## Frontend Readiness Gate

Before a new frontend leans on generated types or strict API clients:

1. Django system checks must pass.
2. OpenAPI schema generation must complete.
3. Schema warnings/errors should be reduced enough that generated clients are
   trustworthy.
4. Authentication, tenant selection, file upload, order lifecycle, payments,
   notifications, and role dashboards need clear canonical endpoints.
5. Deprecated or duplicate endpoints should be marked, removed, or documented.

## Near-Term Cleanup

- Keep Docker Compose backend-only.
- Keep Makefile commands backend-only.
- Treat stale frontend docs as reference until rewritten.
- Continue harmonizing `files_management` and other app APIs around serializers,
  permissions, schema annotations, and domain services.
- Preserve `backend/API_CONTRACT_FRONTEND.md` as the temporary frontend contract
  note until the OpenAPI schema is reliable enough to replace it.
