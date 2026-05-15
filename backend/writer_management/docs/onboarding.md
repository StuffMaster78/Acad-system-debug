# Writer Onboarding Pipeline

## Two onboarding layers

```
accounts.AccountProfile.onboarding_status   ← platform layer
WriterProfile.onboarding_status             ← writer domain layer
```

These are independent. Both must reach `COMPLETED` before a writer
is assignment-eligible.

## Full approval pipeline

```
WriterApplication.submit()
        │
        ▼ Admin reviews
WriterApplicationService.approve()
        │
        ├─ 1. AccountCreationService.create_account_profile()
        │       User created (or found by email)
        │       AccountProfile created
        │
        ├─ 2. WriterOnboardingService.complete_onboarding()
        │       Role 'writer' assigned
        │       'writer_portal' access granted
        │       Tenant access granted
        │       OnboardingSession created + completed
        │       AccountProfile.onboarding_status = COMPLETED
        │       AccountProfile.status = UNDER_REVIEW | ACTIVE
        │
        └─ 3. WriterProfileService.create_for_approved_application()
                WriterProfile created
                WriterProfile.onboarding_status = IN_PROGRESS
                Satellite rows bootstrapped via signal:
                  WriterStatus
                  WriterCapacity
                  WriterDisciplineState
                  WriterAvailabilityPreference
```

## Writer domain onboarding states

```
NOT_STARTED
    │ profile created
IN_PROGRESS
    │ writer submits documents
DOCUMENTS_PENDING
    │ admin accepts docs        │ admin rejects docs
REVIEW_PENDING              REJECTED
    │ admin final approval          │ writer resubmits
COMPLETED               IN_PROGRESS
```

Valid transitions enforced by `WriterProfileService.advance_onboarding_status()`.

## Assignment eligibility

Writer becomes eligible when ALL of:
- `WriterProfile.onboarding_status == COMPLETED`
- `WriterProfile.is_deleted == False`
- `WriterCapacity.can_take_orders == True`
- `WriterCapacity.is_accepting_orders == True`
- `WriterCapacity.active_orders_count < effective_ceiling`
- `WriterDisciplineState.is_suspended == False`
- `WriterDisciplineState.is_blacklisted == False`
- No active `WriterAvailabilityWindow`
