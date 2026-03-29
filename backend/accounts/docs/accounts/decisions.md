# Architectural Decisions

## Why not use ViewSets everywhere?

Because accounts operations are action-based:

- activate
- suspend
- assign role

These are not CRUD operations.

---

## Why separate users and accounts?

Because:

- a user is identity
- an account is contextual membership

This allows multi-tenant systems.

---

## Why services layer?

To:

- isolate business logic (Keep views as thin and dumb as they can be)
- improve testability
- avoid fat views

---

## Why audit logging?

Because:

- accounts affect money and permissions
- every change must be traceable
