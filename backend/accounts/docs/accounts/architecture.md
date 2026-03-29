# Accounts Architecture

## Layers

The accounts app follows a layered architecture:

### Models

Store data only. No business logic.

### Services

Handle all business logic:

- role assignment
- onboarding
- lifecycle transitions

### Selectors

Handle read logic:

- fetching profiles
- checking roles
- building summaries

### API Layer

Handles:

- request validation
- calling services/selectors
- formatting responses

## Key Rule

Views must NEVER contain business logic.

---

## Flow Example

Activate account:

View → Serializer → Service → Model → Audit Log → Response

---

## Why this design

- Testability
- Maintainability
- Clear separation of concerns
- Scalability as system grows
