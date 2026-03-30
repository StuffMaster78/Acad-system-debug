# System Documentation

This directory contains comprehensive documentation for the system.

## Structure

- `architecture/` → System-level design decisions
- `users/` → Users domain (identity, profile, workflows)
- `api/` → API conventions and contracts
- `operations/` → Production, debugging, and safety practices

---

## How to Use this Documentation

### If you are new to the system

Start here:

1. architecture/overview.md
2. architecture/auth_and_users.md
3. users/overview.md

### If you are working on a feature

Go to the relevant domain:

1. Users → users/
2. API → api/
3. System-level → architecture/

### If something broke in production

Check:

1. operations/debugging.md
2. operations/audit_strategy.md

## Documentation Principles

This documentation is designed to:

- Explain **why**, not just what
- Capture **contracts and invariants**
- Prevent regressions and silent design drift
- Support onboarding and debugging

This documentation follows strict principles:

### 1. Explain WHY

Not just what exists, but why it exists.

### 2. Capture Invariants

Things that must never break are explicitly documented.

### 3. Be Operational

Docs should help:

- debugging
- scaling
- onboarding

### 4. Stay Close to Code

Documentation reflects real system behavior, not assumptions.

---

## System Guarantees

Across the system, the following guarantees hold:

- All critical mutations are audited
- All workflows are state-driven
- Multi-tenancy is enforced
- Business logic lives in services, not views

## Maintenance

When modifying system behavior:

- Update the relevant documentation
- Do not introduce undocumented flows
- Keep API contracts consistent

## Final Note

- If the code and docs disagree, the system is already broken.
