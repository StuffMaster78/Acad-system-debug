# Packaging Strategy

## Current Decision (updated May 2026)

**The frontend lives in this repository.** The earlier plan to keep this
backend-only and add the frontend in a separate package has been superseded.
The Vue 3 frontend is now built, feature-complete, and maintained here as a
monorepo alongside the Django backend.

The split-repository target shape described in the original plan (below) remains
a valid future option if the codebase grows to a size where separate CI,
separate deployments, or separate teams make sense. For now, a monorepo with
clear internal boundaries is the right call.

---

## Repository Boundaries (current)

```text
writing_project/
├── backend/     Django API · domain apps · migrations · Celery · OpenAPI
├── frontend/    Vue 3 portals · Pinia stores · TypeScript · Tailwind
├── nginx/       Reverse proxy config
├── docs/        Architecture, API reference, deployment runbooks
└── .github/     CI workflows (backend + frontend), deploy, PR hygiene
```

Each layer has a clear owner:

- **Backend** owns the API contract, database schema, business logic, and
  background tasks. It does not import or depend on frontend code.
- **Frontend** consumes the API. It does not contain business logic that belongs
  in Django. It communicates with the backend exclusively through
  `GET /api/v1/portal-context/` at boot and REST endpoints under `/api/v1/`.
- **nginx** proxies the two. Static assets are served directly; `/api/` is
  forwarded to Django; SSE endpoints get appropriate buffering disabled.

---

## Portal Surface Separation

The frontend is a single build, but it enforces domain-based surface isolation
at runtime via the portal context endpoint. Client websites, the writer domain,
and the staff domain each get a different surface with different allowed routes
and roles. See `README.md` → Portal Architecture for the full mapping.

---

## Frontend Readiness Gates (met)

The following gates from the original strategy have been cleared:

- [x] Django system checks pass
- [x] OpenAPI schema generation completes
- [x] `vue-tsc --noEmit` passes clean
- [x] Authentication, tenant selection, file upload, order lifecycle, payments,
      notifications, and role dashboards have canonical endpoints
- [x] Portal context endpoint live (`GET /api/v1/portal-context/`)
- [x] Payment disclosure wired end-to-end

---

## Original Target Shape (reference)

The original plan described splitting into four packages:

```text
writing-backend/    Django API, domain logic, migrations, OpenAPI schema
writing-frontend/   Fresh portals and dashboards for all user types
writing-infra/      Production deployment, observability, reverse proxy
writing-docs/       Product specs, API guides, design decisions, runbooks
```

This remains a valid future migration path. The internal boundaries enforced
now (backend owns logic, frontend owns UI, nginx owns routing) make a future
split straightforward without requiring a rewrite.
