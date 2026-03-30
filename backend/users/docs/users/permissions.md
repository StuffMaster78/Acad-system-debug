# Users Domain Permissions

## Purpose

This document defines access control rules specific to the `users` domain.

It answers:

- who can view what
- who can submit profile changes
- who can review profile changes
- how tenant boundaries are enforced
- what actions are restricted to request owners or staff

This document is domain-specific.

For broader authorization architecture, see:

- `docs/architecture/auth_and_users.md`

---

## Scope

The users domain permissions apply to:

- approved profile access
- profile update request creation
- request lifecycle actions
- tenant-scoped review operations

They do not define:

- authentication mechanisms
- session validation
- global API auth headers
- system-wide authorization strategy

---

## Permission Model

The users domain uses a combination of:

1. authenticated access
2. object ownership
3. role-based review authority
4. tenant scoping

---

## Core Rules

### 1. Profile ownership matters

A user may access only their own profile-facing resources unless a staff flow explicitly allows otherwise.

---

### 2. Review authority is restricted

Only approved reviewer roles may:

- mark requests under review
- approve requests
- reject requests
- apply approved requests

---

### 3. Tenant boundaries are mandatory

A reviewer may only act on requests belonging to their own `website`, unless they hold a global role.

---

### 4. Cancellation is owner-only

Only the request owner may cancel their own request.

---

## Role Categories

The exact role source may evolve, but the permission logic currently relies on categories like these.

### Request Owners

These are normal end users acting on their own records.

Typical roles:

- client
- writer

---

### Tenant Staff Reviewers

These are internal tenant-scoped staff roles.

Typical roles:

- admin
- editor
- support

These roles may review requests only inside their own tenant.

---

### Global Reviewers

These are cross-tenant or system-wide roles.

Typical role:

- superadmin

These roles may review requests across tenants.

---

## Permission Matrix

| Action | Anonymous | Authenticated User | Request Owner | Tenant Staff Reviewer | Global Reviewer |
|------|-----------|--------------------|---------------|-----------------------|-----------------|
| View own approved profile | No | Yes | Yes | N/A | N/A |
| List own profile update requests | No | Yes | Yes | No | No |
| Submit profile update request | No | Limited to allowed roles | Yes | No | No |
| Cancel request | No | No | Yes | No | No |
| Mark under review | No | No | No | Yes, same tenant only | Yes |
| Approve request | No | No | No | Yes, same tenant only | Yes |
| Reject request | No | No | No | Yes, same tenant only | Yes |
| Apply approved request | No | No | No | Yes, same tenant only | Yes |

---

## Object-Level Rules

### IsProfileOwner

Used when access depends on the current user owning the profile-like object.

The rule is:

```text
object.user == request.user
```

## 

or, for direct user objects:

object == request.user

* * *

### IsProfileUpdateOwner

## 

Used when access depends on the current user owning the `ProfileUpdateRequest`.

The rule is:

request\_obj.user == request.user

* * *

### CanCancelOwnProfileUpdateRequest

## 

Used when a user wants to cancel a request.

The rule is:

-   request must belong to the current user
-   request must be in a cancellable state
-   tenant crossing is not allowed

This permission only answers **who may try** the action.

Workflow state validation remains in the service layer.

* * *

## Action-Level Rules

### Submit Profile Update Request

## 

A user may submit a request only if:

-   they are authenticated
-   their role is allowed to submit
-   they belong to a valid tenant
-   they do not already have an active request

The permission layer covers identity and role.  
The service layer covers workflow invariants.

* * *

### Mark Under Review

## 

A reviewer may mark a request under review only if:

-   they are authenticated
-   they belong to an allowed reviewer role
-   they are authorized for the tenant that owns the request

* * *

### Approve Request

## 

A reviewer may approve a request only if:

-   they are authenticated
-   they belong to an allowed reviewer role
-   they are authorized for the request tenant

The service layer additionally validates the source state.

* * *

### Reject Request

## 

A reviewer may reject a request only if:

-   they are authenticated
-   they belong to an allowed reviewer role
-   they are authorized for the request tenant

The service layer additionally requires a non-empty rejection note.

* * *

### Apply Approved Request

## 

A reviewer or system-controlled actor may apply a request only if:

-   they are authenticated and authorized, or
-   the system explicitly performs the action under a trusted workflow

The service layer additionally checks:

request.status == APPROVED

* * *

## Tenant Enforcement

## 

Tenant enforcement in the users domain is explicit.

### Tenant-Scoped Reviewer Rule

## 

For tenant staff:

request.user.website == reviewer.website

or, where stored directly:

request.website == reviewer.website

* * *

### Global Reviewer Rule

## 

A global role may bypass tenant comparison.

This should be granted sparingly.

* * *

## Service Layer vs Permission Layer

## 

This distinction is important.

### Permission Layer

## 

The permission layer answers:

-   is this actor allowed to attempt this action?

Examples:

-   is the actor authenticated?
-   is the actor the owner?
-   is the actor a reviewer?
-   is the reviewer in the same tenant?

* * *

### Service Layer

## 

The service layer answers:

-   is this action valid right now?

Examples:

-   is the request in the correct state?
-   does a rejection note exist?
-   does the profile belong to the same user?
-   are the requested fields allowed?

* * *

## Why This Split Exists

## 

Because permissions alone are not enough.

Bad design would let permissions decide workflow validity.

Good design separates:

-   **authorization**
-   **business state validation**

This keeps the system predictable and testable.

* * *

## Practical Examples

### Example 1: User Cancels Their Own Request

## 

Allowed when:

-   actor is authenticated
-   actor owns the request

Still blocked if:

-   request is already `APPROVED`
-   request is already `APPLIED`
-   request is already `REJECTED`

Those state checks are not permission checks.  
They are workflow checks.

* * *

### Example 2: Admin Reviews a Request in Another Tenant

## 

Blocked when:

-   reviewer is tenant-scoped staff
-   request belongs to a different website

Allowed when:

-   reviewer is global reviewer

* * *

### Example 3: Authenticated User Tries to Approve Request

## 

Blocked because:

-   authenticated access is not enough
-   reviewer role is required

* * *

## Security Guarantees

## 

The users domain permissions guarantee that:

1.  normal users cannot review requests
2.  reviewers cannot cross tenant boundaries unless globally authorized
3.  owners retain control over their own pending requests
4.  sensitive profile changes cannot be mutated directly

* * *

## Failure Scenarios

## 

| Scenario | Outcome |
| --- | --- |
| Anonymous request | Denied |
| Wrong tenant reviewer | Denied |
| Non-owner tries to cancel | Denied |
| Normal user tries to approve | Denied |
| Global reviewer acts across tenant | Allowed if role permits |

* * *

## Anti-Patterns

## 

Avoid:

-   checking only `is_authenticated`
-   letting views do tenant authorization inline everywhere
-   relying only on frontend role checks
-   mixing workflow validation into permission classes
-   silently bypassing object-level permission checks

* * *

## Recommended Usage Pattern

## 

Views should:

1.  declare base permission classes
2.  choose action-specific permission classes
3.  fetch the object
4.  run `check_object_permissions(...)`
5.  delegate to the service layer

This keeps access control explicit and consistent.

* * *

## Summary

## 

The users domain permissions enforce:

-   ownership rules
-   reviewer authority
-   tenant isolation
-   safe workflow access

They do not replace service-layer business validation.

* * *

## Final Principle

## 

> Permissions decide who may act.  
> Services decide whether the action is valid.
