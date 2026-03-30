# Users Domain Overview

## Purpose

The `users` domain is responsible for:

- Identity representation (`User`)
- Profile management (`UserProfile`)
- Controlled profile mutation workflows
- Privacy and user-controlled data changes
- Integration with audit logging and tenancy

---

## Design Philosophy

This system enforces:

1. **Controlled mutation**
   - Users cannot directly mutate sensitive profile data.
   - Changes go through a review workflow.

2. **Auditability**
   - Every meaningful action is logged.
   - State transitions are explicit and traceable.

3. **Multi-tenancy awareness**
   - All user operations are scoped to a `website`.

4. **Separation of concerns**
   - Models → state representation
   - Services → business logic and workflows
   - APIs → transport (Request/response handling)
   - Audit → cross-cutting concern/traceability

---

## Core Concepts

### 1. User

Represents authentication identity.

Responsibilities:

- Authentication identity anchor
- Tenant association
- Minimal user-level data

### 2. UserProfile

Represents mutable user-facing attributes.

Responsibilities

- Display data (name, bio, avatar)
- Localization (timezone, locale)
- Non-sensitive user metadata

### 3. ProfileUpdateRequest

Represents a controlled mutation request.

Responsibilities:

- Store proposed changes
- Track lifecycle status
- Capture review decisions
- Ensure safe application of changes

---

### State Machine

PENDING → UNDER_REVIEW → APPROVED → APPLIED
       ↘ REJECTED
       ↘ CANCELLED

## Key Guarantee

> No sensitive profile field is mutated without going through a controlled workflow.

---

## Invariants

The following must always hold:

1. A user cannot have more than one active request
2. Only approved requests can be applied
3. All transitions must be audited
4. All operations must respect tenant boundaries
5. Profile changes must be explicit and traceable

## High-Level Flow

```text
User submits changes
    ↓
ProfileUpdateRequest created (PENDING)
    ↓
Staff reviews → UNDER_REVIEW
    ↓
Approve → APPROVED
    ↓
Apply → APPLIED → Profile updated


## Data Ownership

## 

Website (tenant)  
    ↓  
User  
    ↓  
UserProfile  
    ↓  
ProfileUpdateRequest

* * *

## Interaction with Other Domains

### Authentication

## 

-   Resolves identity (`User`)
-   Does not mutate profile

* * *

### Accounts (Authorization)

## 

-   Determines access permissions
-   Does not manage profile state

* * *

### Audit Logging

## 

-   Records all state transitions
-   Stores field-level diffs
-   Provides traceability

* * *

### Notifications (Future)

## 

-   Informs users of changes
-   Triggered by workflow events

* * *

## Failure Scenarios

## 

| Scenario | Outcome |
| --- | --- |
| Duplicate active request | Blocked |
| Invalid fields | Validation error |
| Unauthorized action | Permission denied |
| Apply without approval | Blocked |
| Cross-tenant access | Denied |

* * *

## Design Decisions

### Why not allow direct profile updates?

## 

To enforce:

-   validation
-   review
-   auditability

* * *

### Why use a request workflow?

## 

To make profile changes:

-   controlled
-   traceable
-   reversible (conceptually)

* * *

### Why store changes as JSON?

## 

To:

-   support flexible schema evolution
-   capture diffs easily
-   simplify audit logging

* * *

## Future Extensions

## 

Planned enhancements include:

-   Profile versioning
-   Privacy controls and consent tracking
-   Data export endpoints (GDPR-style)
-   Login alerts and security signals
-   Integration with authentication state (MFA, sessions)

* * *

## Summary

## 

The users domain provides:

-   identity representation
-   controlled profile mutation
-   tenant-aware data handling
-   audit-integrated workflows

* * *

## Final Principle

## 

> If profile data can change without a trace, the system is already compromised.
