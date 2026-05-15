# writer_management

Django app for managing writers on the academic writing marketplace platform.

## Overview

`writer_management` is the domain app that owns everything about a writer's
identity, operational state, discipline, performance, and recognition on the
platform. It is the second layer in the identity chain:

```
auth.User
  └── accounts.AccountProfile
        └── writer_management.WriterProfile   ← this app
```

Writers are onboarded through `WriterApplication`, approved via
`WriterApplicationService`, and assigned a `WriterProfile` linked to their
`AccountProfile`. Everything else — discipline, performance, availability,
rewards — hangs off `WriterProfile`.

---

## Documentation

| Document | Description |
|---|---|
| [Architecture](architecture.md) | App boundaries, dependency graph, design decisions |
| [Models](models.md) | All models with field reference and ownership rules |
| [Services](services.md) | All services with method signatures and call contracts |
| [API](api.md) | All endpoints, permissions, request/response shapes |
| [Onboarding](onboarding.md) | Writer onboarding pipeline and accounts integration |
| [Discipline](discipline.md) | Warning, strike, suspension, blacklist, probation flows |
| [Performance](performance.md) | Metrics pipeline, composite score, level progression |
| [Notifications](notifications.md) | Event keys, context variables, template registry |
| [Celery Tasks](tasks.md) | All scheduled tasks, schedules, and ordering |

---

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...
    "writer_management.apps.WriterManagementConfig",
]
```

### Run migrations

```bash
python manage.py makemigrations writer_management
python manage.py migrate
```

### Mount URLs

```python
# project/urls.py
urlpatterns = [
    ...
    path(
        "api/writer-management/",
        include("writer_management.api.urls", namespace="writer_management"),
    ),
]
```

### Seed site config

```bash
python manage.py seed_writer_config --website-id=1
```

---

## Key Concepts

### Identity chain

```bash
WriterApplication (pre-onboarding)
  ↓  approved
accounts.AccountProfile (platform identity)
  ↓  linked
WriterProfile (writer domain identity)
  ↓  bootstraps via signal
WriterStatus          — online presence
WriterCapacity        — workload state
WriterDisciplineState — cached discipline summary
WriterAvailabilityPreference — standing preferences
```

### Two onboarding layers

`accounts` owns platform onboarding (role, portal, tenant access).
`writer_management` owns writer domain onboarding (documents, review, level).
See [onboarding.md](onboarding.md) for the full pipeline.

### Discipline model

Warnings are temporary and expire. Strikes are permanent.
Both feed into `WriterDisciplineState` (the cache) via `WriterStatusService.recompute()`.
See [discipline.md](discipline.md).

### Performance pipeline

Weekly Celery task → snapshots → composite scores → percentile ranks → level progression.
See [performance.md](performance.md).

---

## App boundaries

This app does **not** own:

| Concern | Owner |
|---|---|
| Rate card snapshots | `writer_compensation` |
| Tip splits | `tips` |
| Order requests / takes | `order_actions` |
| File uploads | `files_management` |
| Ratings | `reviews_system` |
| Messaging | `messaging` |
| Support tickets | `support` |
