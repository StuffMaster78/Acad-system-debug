# Notifications

## Architecture

`writer_management` never renders templates or selects delivery channels.
Every notification call delegates to `NotificationService` in
`notifications_system`.

```
writer_management service
        │
        └─ NotificationService.notify(event_key, recipient, website, context)
                │
                └─ notifications_system owns:
                     Template rendering
                     Channel selection (email, in-app, SMS, push)
                     User preferences / DND / mute
                     Outbox deduplication
                     Celery delivery queue
```

## Calling patterns

```python
# Single user (must be authenticated User instance)
NotificationService.notify(
    event_key="writer.discipline.warning_issued",
    recipient=user,
    website=website,
    context={"registration_id": "WR-...", "reason": "..."},
    triggered_by=admin_user,
    is_critical=False,
)

# All admins on a website
NotificationService.notify_role(
    event_key="writer.application.submitted",
    role="admin",
    website=website,
    context={"full_name": "...", "email": "..."},
)
```

## Event key registry

Every event key must be registered in `notifications_system.enums.NotificationEvent`.
The full registry for `writer_management` is in `writer_management/notifications.py`.

### Discipline — sent to writer

| Event key | Trigger |
|---|---|
| `writer.discipline.warning_issued` | Warning created |
| `writer.discipline.warning_voided` | Warning voided |
| `writer.discipline.strike_issued` | Strike created |
| `writer.discipline.strike_voided` | Strike voided |
| `writer.discipline.suspended` | Suspension created |
| `writer.discipline.suspension_lifted` | Suspension lifted |
| `writer.discipline.blacklisted` | Blacklist created |
| `writer.discipline.blacklist_lifted` | Blacklist lifted |
| `writer.discipline.probation_placed` | Probation created |
| `writer.discipline.probation_ended` | Probation ended |
| `writer.discipline.penalty_applied` | Penalty applied |

### Discipline — sent to admins

| Event key | Trigger |
|---|---|
| `writer.discipline.warning_threshold_reached` | Active warning count crosses threshold |

### Level

| Event key | Trigger |
|---|---|
| `writer.level.promoted` | Level progression promotion |
| `writer.level.demoted` | Level progression demotion |

### Rewards

| Event key | Trigger |
|---|---|
| `writer.reward.granted` | Reward evaluated and granted |

### Availability

| Event key | Trigger |
|---|---|
| `writer.availability.window_declared` | Writer declares unavailability |
| `writer.availability.window_ended` | Window ended (manually or expired) |

### Pen name

| Event key | Trigger | Recipient |
|---|---|---|
| `writer.pen_name.request_submitted` | Writer submits request | Admins |
| `writer.pen_name.request_approved` | Admin approves | Writer |
| `writer.pen_name.request_rejected` | Admin rejects | Writer |

### Onboarding

| Event key | Trigger |
|---|---|
| `writer.onboarding.documents_requested` | Status → DOCUMENTS_PENDING |
| `writer.onboarding.under_review` | Status → REVIEW_PENDING |
| `writer.onboarding.completed` | Status → COMPLETED |
| `writer.onboarding.rejected` | Status → REJECTED |

### Applications

| Event key | Trigger | Recipient |
|---|---|---|
| `writer.application.submitted` | Application submitted | Admins |
| `writer.application.approved` | Admin approves | Writer (User) |
| `writer.application.rejected` | Admin rejects | Applicant (email) |
| `writer.application.withdrawn` | Applicant withdraws | Applicant (email) |

## Context variables per event

### `writer.discipline.warning_issued`
```python
{
    "registration_id":      str,
    "category":             str,   # human-readable label
    "reason":               str,
    "issued_at":            str,   # ISO 8601
    "expires_at":           str | None,
    "days_remaining":       int | None,
    "active_warning_count": int,
}
```

### `writer.discipline.suspended`
```python
{
    "registration_id": str,
    "reason":          str,
    "end_date":        str | None,   # None = indefinite
    "auto_triggered":  bool,
    "duration_days":   int | None,
}
```

### `writer.application.approved`
```python
{
    "full_name":       str,
    "registration_id": str,
    "email":           str,
}
```

### `writer.application.rejected`
```python
{
    "full_name":        str,
    "email":            str,
    "rejection_reason": str,
}
```

## Pre-User notifications

At application submission and rejection time, the applicant may not
have a `User` account yet. `NotificationService.notify()` requires
an authenticated `User` — it cannot be used here.

`WriterApplicationService` handles this via:

1. Check if a `User` exists for the email → use `notify()` if so.
2. If no `User` → `EmailService.send_rendered()` with a manually
   constructed rendered dict (subject + body_text).
3. If `EmailService` unavailable → Django `send_mail()` as final fallback.

## Notification failures

All `notify()` calls are wrapped in `try/except` in the service layer.
A notification failure **never** rolls back a discipline action or
application state change. Failures are logged at `WARNING` or `ERROR`
level and monitored separately.
