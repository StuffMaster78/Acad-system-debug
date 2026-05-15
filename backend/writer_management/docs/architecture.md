# Architecture

## App boundaries

`writer_management` answers exactly two questions per model:

1. Who is this writer? (identity)
2. What is their current state? (operational)

Everything else is delegated.

## Dependency graph

```
                    ┌─────────────────────┐
                    │      accounts        │
                    │  AccountProfile      │
                    │  WriterOnboarding    │
                    │  Service             │
                    └──────────┬──────────┘
                               │ OneToOne
                    ┌──────────▼──────────┐
                    │  writer_management  │
                    │  WriterProfile      │◄──── WriterApplication
                    │  (this app)         │
                    └──────┬──────────────┘
           ┌───────────────┼──────────────────────┐
           │               │                      │
  ┌────────▼─────┐ ┌───────▼────────┐ ┌──────────▼───────┐
  │ order_actions│ │writer_compensat│ │  reviews_system  │
  │ assignments  │ │ion rate cards  │ │  WriterRating    │
  └──────────────┘ └────────────────┘ └──────────────────┘
```

## Inbound dependencies (apps that import from us)

- `order_actions` — reads `WriterProfile`, `WriterCapacity`
- `writer_compensation` — reads `WriterProfile` for `RateCardSnapshot`
- `reviews_system` — reads `WriterProfile` for `WriterRating`
- `tips` — reads `WriterProfile` via `User.account_profile.writer_profile`

## Outbound dependencies (apps we import from)

- `accounts` — `AccountProfile`, `AccountCreationService`,
  `WriterOnboardingService`
- `notifications_system` — `NotificationService`
- `orders` — read-only queries for performance reconciliation
- `files_management` — `files_app_file_id` reference on `WriterResource`

## Design principles

### 1. Low-volatility profile

`WriterProfile` changes only on:
- Level assignment / change
- Verification status update
- Onboarding status progression
- Soft delete / restore
- Bio, qualifications, pen name update

High-churn state lives on separate models:
- `WriterCapacity` — order counters (updated on every assignment)
- `WriterStatus` — presence (updated on every heartbeat)
- `WriterDisciplineState` — discipline cache (updated after every discipline event)

This eliminates lock contention on the profile row during assignment routing.

### 2. Cache + source of truth separation

`WriterDisciplineState` is a **cache**, not a source of truth.
Source records are: `WriterWarning`, `WriterStrike`, `WriterSuspension`,
`WriterBlacklist`, `WriterProbation`.

`WriterStatusService.recompute()` rebuilds the cache after every mutation.
Never write to `WriterDisciplineState` directly.

### 3. Services own mutations, models own structure

Models do not contain business logic, `save()` overrides with side effects,
or cross-model operations. Services own all of that.

```
✓ Model:   field definitions, constraints, simple properties
✓ Service: create, update, validate, coordinate, notify
✗ Model:   calling other services, sending notifications, HTTP calls
```

### 4. Notifications delegated entirely

`writer_management` never renders templates or selects delivery channels.
Every notification call goes to `NotificationService.notify()` or
`NotificationService.notify_role()`. Templates live in `notifications_system`.

### 5. Two onboarding statuses, two owners

```
AccountProfile.onboarding_status  ← accounts app
WriterProfile.onboarding_status   ← writer_management
```

They track different things. See [onboarding.md](onboarding.md).

## Directory structure

```
writer_management/
├── api/
│   ├── filters/
│   │   └── writer_filters.py
│   ├── serializers/
│   │   ├── profile_serializer.py
│   │   ├── discipline_serializer.py
│   │   ├── application_serializer.py
│   │   ├── availability_serializer.py
│   │   ├── performance_serializer.py
│   │   ├── reward_serializer.py
│   │   ├── note_serializer.py
│   │   └── resource_serializer.py
│   ├── views/
│   │   ├── profile_views.py
│   │   ├── discipline_views.py
│   │   ├── availability_views.py
│   │   ├── performance_views.py
│   │   ├── reward_views.py
│   │   ├── note_views.py
│   │   ├── resource_views.py
│   │   └── application_views.py
│   ├── permissions.py
│   └── urls.py
├── models/
│   ├── writer_profile.py
│   ├── writer_level.py
│   ├── writer_level_settings.py
│   ├── writer_level_criteria.py
│   ├── writer_level_history.py
│   ├── writer_status.py
│   ├── writer_discipline_state.py
│   ├── writer_capacity.py
│   ├── availability.py
│   ├── writer_warning.py
│   ├── writer_strike.py
│   ├── discipline.py
│   ├── performance.py
│   ├── rewards.py
│   ├── resources.py
│   ├── pen_name.py
│   ├── configs.py
│   ├── logs.py
│   ├── writer_note.py
│   ├── writer_application.py
│   └── __init__.py
├── services/
│   ├── discipline_service.py
│   ├── discipline_notification_service.py
│   ├── writer_warning_service.py
│   ├── status_service.py
│   ├── assignment_eligibility_service.py
│   ├── availability_service.py
│   ├── writer_config_service.py
│   ├── composite_score_service.py
│   ├── performance_tracker_service.py
│   ├── writer_metrics_snapshot_service.py
│   ├── performance_aggregator_service.py
│   ├── level_progression_service.py
│   ├── reward_evaluation_service.py
│   ├── writer_profile_service.py
│   ├── writer_application_service.py
│   ├── writer_note_service.py
│   ├── pen_name_service.py
│   ├── writer_activity_service.py
│   ├── writer_ip_service.py
│   ├── resource_service.py
│   ├── writer_action_log_service.py
│   ├── writer_reconciliation_service.py
│   └── __init__.py
├── tasks/
│   ├── availability_tasks.py
│   ├── performance_tasks.py
│   └── reward_tasks.py
├── apps.py
├── admin.py
├── constants.py
├── enums.py
├── exceptions.py
├── notifications.py
├── signals.py
└── utils.py
```
