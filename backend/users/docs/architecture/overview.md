# System Architecture Overview

## Core Domains

| Domain | Responsibility |

|------|--------------|

| users | identity + profile management |
| accounts | roles + permissions + authorization |
| authentication | login, sessions, MFA |
| audit_logging | system-wide traceability |
| notifications | user communication and alerts |
| payments | Financial Transaction and Ledger |

---

## Design Principles

The system follows a **layered architecture with domain separation**.

### Layers

API Layer -> Service Layer -> Model Layer -> Infrastructure

#### API Layer

- Handles HTTP requests
- Serializes/deserializes data
- Delegates logic to services

**No business logic lives here.**

#### Service Layer

- Contains business logic
- Enforces workflows and rules
- Coordinates models and side effects

**This is the brain of the system.**

#### Model Layer

- Defines database structure
- Holds minimal logic
- Represents system state

#### Infrastructure Layer

- Celery (async processing)
- Database
- Logging systems
- External integrations

## Key Design Principles

### 1. Separation of Concerns

Each layer has a strict responsibility:

- Models -> state
- Services -> business logic
- APIs -> transport
- Audit -> cross-cutting

---

### 2. Explicit Workflows

All critical processes are modeled as state machines, not ad hoc logic.
Every critical change goes through a defined lifecycle.
Example:

``` bash
Profile Update:
PENDING → UNDER_REVIEW → APPROVED → APPLIED
```

---

### 3. Multi-Tenancy First

All user-facing operations are scoped by `website`.

Example: User -> Website -> Data

No operation should cross tenant boundaries.

---

### 4. Auditability

> If it matters, it must be traceable.
Every important action is logged.

- Service -> AuditLogService -> Celery -> Database

### 5. Async Where Necessary

Non-critical operations are handled asynchronously:

- Audit logging
- Notifications (future)

---

## Data Flow Example

```text
API → Service → Model → AuditLog → Async Task
```

Profile Update Flow Example:

``` text
Client Request
    ↓
API View
    ↓
Service Layer (validation + workflow)
    ↓
Model Update
    ↓
AuditLogService
    ↓
Celery Task (async)
    ↓
Database (AuditLogEntry)
```

### Cross-Cutting Concerns

These apply across all domains:

#### Audit Logging

- Centralized logging system
- Tracks all state changes
- Supports debugging and compliance

#### Notifications

- Event-driven communication layer
- Sends user alerts (email, SMS, etc.)

#### Security

- Authentication handled separately
- Authorization handled via roles
- Sensitive operations require validation

#### System Boundaries

##### Internal

- Django apps (users, accounts, etc.)
- Services
- Database

##### External (future)

- Payment gateways
- Email/SMS providers
- Analytics systems

##### Failure Handling Strategy

- Layer -> Behavior
- API -> Return structured error
- Service -> Raise validation/domain errors
- Audit -> Never break main flow
- Async tasks -> Retry on failure

#### Scaling Strategy

##### Current

- Single database
- Async tasks via Celery

##### Future

- Audit log partitioning
- Event streaming (Kafka, etc.)
- Read replicas
- Service decomposition

#### Anti-Patterns Avoided

- Fat views
- Business logic in serializers
- Silent mutations
- Cross-domain coupling
- Missing audit trails

### Summary

The system is designed to be:

- Predictable
- Traceable
- Maintainable
- Scalable

## Final Principle

If a system cannot explain what happened, it cannot be trusted.
