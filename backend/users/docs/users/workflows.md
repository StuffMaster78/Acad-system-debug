# Users Domain Workflows

## Purpose

This document defines the core workflows governing profile updates.

These workflows enforce:

- controlled mutation
- auditability
- validation
- role-based review

---

## Core Workflow

### Profile Update Lifecycle

```text
PENDING → UNDER_REVIEW → APPROVED → APPLIED
       ↘ REJECTED
       ↘ CANCELLED
```

## Workflow: Submit Profile Update

### Actor

## 

User

* * *

### Description

## 

User submits a request to modify profile data.

* * *

### Steps

## 

1.  Validate requested fields
2.  Ensure no active request exists
3.  Create ProfileUpdateRequest
4.  Set status → `PENDING`
5.  Log audit event

* * *

### Constraints

## 

-   Only allowed fields can be updated
-   Only one active request per user

* * *

### Audit Event

## 

profile\_update\_submitted

* * *

## Workflow: Mark Under Review

### Actor

## 

Staff

* * *

### Description

## 

Staff begins reviewing a request.

* * *

### Steps

## 

1.  Validate current status is `PENDING`
2.  Set status → `UNDER_REVIEW`
3.  Set reviewer
4.  Log audit event

* * *

### Audit Event

## 

profile\_update\_marked\_under\_review

* * *

## Workflow: Approve Request

### Actor

## 

Staff

* * *

### Description

## 

Staff approves a request.

* * *

### Steps

## 

1.  Validate status is:
    -   `PENDING` or
    -   `UNDER_REVIEW`
2.  Set status → `APPROVED`
3.  Set reviewer + timestamp
4.  Store optional review note
5.  Log audit event

* * *

### Audit Includes

## 

-   status transition
-   reviewer identity
-   review note

* * *

### Audit Event

## 

profile\_update\_approved

* * *

## Workflow: Reject Request

### Actor

## 

Staff

* * *

### Description

## 

Staff rejects a request.

* * *

### Steps

## 

1.  Validate status is:
    -   `PENDING` or
    -   `UNDER_REVIEW`
2.  Require review note
3.  Set status → `REJECTED`
4.  Set reviewer + timestamp
5.  Log audit event

* * *

### Audit Includes

## 

-   status transition
-   rejection reason

* * *

### Audit Event

## 

profile\_update\_rejected

* * *

## Workflow: Cancel Request

### Actor

## 

User (owner only)

* * *

### Description

## 

User cancels their own request.

* * *

### Steps

## 

1.  Validate ownership
2.  Validate status is:
    -   `PENDING` or
    -   `UNDER_REVIEW`
3.  Set status → `CANCELLED`
4.  Log audit event

* * *

### Audit Event

## 

profile\_update\_cancelled

* * *

## Workflow: Apply Approved Request

### Actor

## 

Staff or System

* * *

### Description

## 

Approved changes are applied to the user profile.

* * *

### Steps

## 

1.  Validate status is `APPROVED`
2.  Load profile
3.  Iterate over requested\_changes
4.  Apply changes to profile
5.  Capture field-level diffs
6.  Save profile
7.  Set request status → `APPLIED`
8.  Set applied timestamp
9.  Log audit event

* * *

### Audit Includes

## 

-   field-level changes
-   request status transition

* * *

### Example Changes

## 

{  
  "display\_name": {  
    "from": "Old",  
    "to": "New"  
  },  
  "\_\_request\_status\_\_": {  
    "from": "approved",  
    "to": "applied"  
  }  
}

* * *

### Audit Event

## 

profile\_update\_applied

* * *

## Validation Rules

### Allowed Fields

## 

Only predefined fields can be updated:

-   display\_name
-   bio
-   avatar
-   timezone
-   locale
-   country

* * *

### Invalid Requests

## 

Rejected if:

-   unknown fields are present
-   values are invalid
-   request duplicates an active one

* * *

## State Transition Rules

## 

| From | To | Allowed |
| --- | --- | --- |
| PENDING | UNDER\_REVIEW | Yes |
| PENDING | APPROVED | Yes |
| UNDER\_REVIEW | APPROVED | Yes |
| UNDER\_REVIEW | REJECTED | Yes |
| PENDING | REJECTED | Yes |
| PENDING | CANCELLED | Yes |
| UNDER\_REVIEW | CANCELLED | Yes |
| APPROVED | APPLIED | Yes |
| Any | Invalid state | No |

* * *

## Invariants

## 

Must always hold:

1.  Only approved requests can be applied
2.  Only owner can cancel
3.  Only staff can approve/reject
4.  All transitions must be audited
5.  Profile changes must match requested\_changes exactly

* * *

## Failure Scenarios

## 

| Scenario | Outcome |
| --- | --- |
| Apply without approval | Blocked |
| Cancel by non-owner | Blocked |
| Invalid status transition | Blocked |
| Missing review note on reject | Blocked |
| Missing profile | System error |

* * *

## System Interaction

### Audit Logging

## 

Every workflow step triggers:

AuditLogService.log\_auto(...)

* * *

### Notifications (Future)

## 

Each event can trigger notifications:

-   submission → notify staff
-   approval/rejection → notify user
-   apply → notify user

* * *

## Design Decisions

### Why separate approve and apply?

## 

Because:

-   Approval = decision
-   Apply = mutation

This allows:

-   delayed application
-   manual verification
-   batching

* * *

### Why store diffs?

## 

To:

-   reconstruct changes
-   debug issues
-   support compliance

* * *

## Anti-Patterns

## 

Avoid:

-   updating profile inside approve()
-   skipping validation
-   bypassing service layer
-   mutating models directly in views

* * *

## Summary

## 

The workflow ensures:

-   safe profile updates
-   clear state transitions
-   full audit traceability
-   strong validation

* * *

## Final Principle

## 

> Every state transition must be intentional, validated, and traceable.
