
# Users Domain Audit Logging

## Purpose

This document defines how audit logging is used within the `users` domain.

It answers:

- which events are logged
- what data is captured
- why audit logging exists in this workflow
- what guarantees the users domain provides

This document is domain-specific.

For system-wide audit architecture, see:

- `docs/architecture/audit_logging.md`

---

## Why Audit Logging Exists in the Users Domain

The users domain handles identity-adjacent and profile-related state.

That makes it sensitive.

Profile changes may affect:

- public representation
- trust and fraud controls
- internal review workflows
- user support investigations
- compliance and dispute handling

Because of that, the users domain must provide a full trace of meaningful actions.

---

## Core Principle

> No meaningful profile workflow action should happen without an audit trace.

---

## What Is Audited

The users domain audits workflow events, not just raw database writes.

This distinction matters.

### Raw database change

A database row changed.

### Domain event

A user submitted a request, a reviewer approved it, or a profile change was applied.

The users domain cares about domain events.

---

## Audited Events

The following domain events must be logged.

| Event | Meaning |

|------|--------|
| profile_update_submitted | User submitted a profile update request |
| profile_update_marked_under_review | Reviewer began review |
| profile_update_approved | Reviewer approved request |
| profile_update_rejected | Reviewer rejected request |
| profile_update_cancelled | Owner cancelled request |
| profile_update_applied | Approved changes were applied to live profile |

---

## Where Audit Logging Happens

Audit logging is triggered from the service layer.

This is important.

### Correct location

```text
users/services/profile_update_service.py# Audit Logging (Users Domain)
```

## Example Audit Entry

```json
{
  "action": "profile_update_applied",
  "actor_id": 10,
  "target": "users.UserProfile",
  "changes": {
    "display_name": {
      "from": "Old",
      "to": "New"
    },
    "__request_status__": {
      "from": "approved",
      "to": "applied"
    }
  }
}
```

### Incorrect locations

## 

-   views
-   serializers
-   model `save()` methods
-   frontend clients

The service layer is the correct place because it understands:

-   intent
-   workflow state
-   actor
-   target
-   side effects

* * *

## Audit Payload Structure

## 

Each audit entry should capture:

-   `action`
-   `actor`
-   `target`
-   `metadata`
-   `changes`
-   `notes` when relevant

* * *

## Standard Metadata Fields

## 

The users domain should consistently include the following metadata where relevant:

| Field | Meaning |
| --- | --- |
| website\_id | Tenant identifier |
| subject\_user\_id | User affected by the action |
| profile\_update\_request\_id | Request identifier |
| requested\_fields | Requested profile fields |

Using stable metadata keys matters for searchability and reporting.

* * *

## Event-by-Event Guidance

### 1\. profile\_update\_submitted

#### Trigger

## 

When a user creates a new `ProfileUpdateRequest`.

#### Actor

## 

The request owner.

#### Target

## 

`ProfileUpdateRequest`

#### Metadata

## 

Should include:

-   `website_id`
-   `requested_fields`

#### Changes

## 

Usually not required as a status transition, since the request is being created.

* * *

### 2\. profile\_update\_marked\_under\_review

#### Trigger

## 

When a reviewer moves a request from `PENDING` to `UNDER_REVIEW`.

#### Actor

## 

Reviewer.

#### Target

## 

`ProfileUpdateRequest`

#### Metadata

## 

Should include:

-   `website_id`
-   `subject_user_id`

#### Changes

## 

Should include:

{  
  "status": {  
    "from": "pending",  
    "to": "under\_review"  
  }  
}

* * *

### 3\. profile\_update\_approved

#### Trigger

## 

When a reviewer approves a request.

#### Actor

## 

Reviewer.

#### Target

## 

`ProfileUpdateRequest`

#### Metadata

## 

Should include:

-   `website_id`
-   `subject_user_id`

#### Changes

## 

Should include the status transition.

#### Notes

## 

May include the reviewer note.

* * *

### 4\. profile\_update\_rejected

#### Trigger

## 

When a reviewer rejects a request.

#### Actor

## 

Reviewer.

#### Target

## 

`ProfileUpdateRequest`

#### Metadata

## 

Should include:

-   `website_id`
-   `subject_user_id`

#### Changes

## 

Should include the status transition.

#### Notes

## 

Should include the rejection reason.

* * *

### 5\. profile\_update\_cancelled

#### Trigger

## 

When the owner cancels their own request.

#### Actor

## 

Owner.

#### Target

## 

`ProfileUpdateRequest`

#### Metadata

## 

Should include:

-   `website_id`
-   `subject_user_id`

#### Changes

## 

Should include the status transition.

* * *

### 6\. profile\_update\_applied

#### Trigger

## 

When an approved request is applied to the live `UserProfile`.

#### Actor

## 

Reviewer or trusted fallback actor.

#### Target

## 

`UserProfile`

#### Metadata

## 

Should include:

-   `website_id`
-   `profile_update_request_id`
-   `subject_user_id`

#### Changes

## 

This is the most important audit event in the workflow.

It should include:

1.  field-level diffs for each changed profile field
2.  the request status transition from `approved` to `applied`

Example:

{  
  "display\_name": {  
    "from": "Old Name",  
    "to": "New Name"  
  },  
  "bio": {  
    "from": "Old bio",  
    "to": "New bio"  
  },  
  "\_\_request\_status\_\_": {  
    "from": "approved",  
    "to": "applied"  
  }  
}

* * *

## Why Field-Level Diffs Matter

## 

Field-level diffs make it possible to answer:

-   what exactly changed?
-   who changed it?
-   when was it changed?
-   did the live profile match the approved request?

Without diffs, audit logs become vague event markers instead of usable evidence.

* * *

## Relationship to Workflow State

## 

Audit logs do not replace workflow state.

They complement it.

### Workflow state answers

## 

What is the current truth?

### Audit log answers

## 

How did the system get here?

You need both.

* * *

## Relationship to Model Signals

## 

The system may also use generic model-level audit or signal-based logging.

That is fine as a background safety net.

But for the users domain, the important audit records must come from explicit service-layer logging, because only the service layer knows:

-   the workflow step
-   the meaning of the action
-   the correct actor
-   the correct metadata
-   the correct before/after semantics

Signal-only logging is not enough.

* * *

## Tenant Context

## 

Every users-domain audit event should be tenant-aware.

At minimum, user workflow audit events should include:

{  
  "website\_id": 1  
}

This is necessary for:

-   tenant support investigations
-   filtering and reporting
-   incident response

* * *

## Notes and Reviewer Comments

## 

Reviewer notes should be captured when relevant.

### Examples

## 

-   approval rationale
-   rejection reason
-   internal review context

These belong in `notes` or in structured metadata depending on system conventions.

* * *

## Failure Handling

## 

Audit logging must never silently break the main workflow, but failures must still be visible operationally.

### Desired behavior

## 

-   business action succeeds
-   audit logging attempts to record event
-   audit logging failures are logged and observable
-   async retries happen where supported

The users domain depends on audit logging, but must not collapse if the audit path has transient issues.

* * *

## Querying Audit History

## 

Typical queries for the users domain include:

-   all audit events for a profile update request
-   all profile mutation events for a user
-   all workflow events for a website
-   all rejected requests with notes
-   all profile updates applied within a time window

This is why consistent metadata keys matter.

* * *

## Anti-Patterns

## 

Avoid:

-   logging only generic create/update/delete noise
-   skipping field-level diffs on apply
-   logging from views instead of services
-   recording sensitive raw secrets
-   inventing inconsistent metadata keys across events

* * *

## Testing Expectations

## 

Tests for the users domain should verify that audit logs are created for:

-   submit
-   mark under review
-   approve
-   reject
-   cancel
-   apply

Where practical, tests should assert:

-   correct action name
-   correct actor
-   correct target
-   correct metadata
-   correct status transitions
-   correct field diffs on apply

* * *

## Guarantees

## 

The users domain audit strategy guarantees that:

1.  every meaningful workflow step is recorded
2.  state transitions are explicit
3.  applied profile changes are reconstructable
4.  tenant context is preserved
5.  reviewer actions are attributable

* * *

## Summary

## 

The users domain does not treat audit logging as optional decoration.

It is part of the workflow contract.

Without it, profile mutation would be functional but not trustworthy.

* * *

## Final Principle

## 

> In the users domain, a change that cannot be traced is a change that should not exist.

