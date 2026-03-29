# Accounts Models

## AccountProfile

Represents a user within a website.

Key fields:

- status
- onboarding_status
- is_primary

---

## RoleDefinition

Defines roles per website.

Examples:

- client
- writer
- admin
- superadmin
- editors
- content_managers
- support

---

## AccountRole

Links an account profile to a role.

Supports:

- multiple roles per account
- activation/deactivation

---

## AccountAuditLog

Tracks all important account events:

- role assignment
- onboarding
- status changes

---

## AccountStatusHistory

Tracks status transitions over time.

---

## OnboardingSession

Tracks onboarding processes:

- client onboarding
- writer onboarding
- staff onboarding
