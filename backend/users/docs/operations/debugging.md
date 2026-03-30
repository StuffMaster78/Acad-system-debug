# Debugging and Incident Response

## Purpose

This document defines how to debug issues and respond to incidents in the system.

It provides:

- a structured debugging approach
- common failure scenarios
- investigation workflows
- practical playbooks

This is an operations-level guide.

---

## Core Principle

> Do not guess. Trace.

---

## Debugging Mindset

Always follow this order:

```text
What happened?
    ↓
Where did it happen?
    ↓
Why did it happen?
    ↓
Can we reproduce it?
    ↓
How do we prevent it?
```

## Debugging Layers

## 

The system can be debugged across layers:

| Layer | What to Check |
| --- | --- |
| API | Request/response, status codes |
| Service | Business logic, state transitions |
| Model | Data integrity |
| Audit Logs | What actually happened |
| Celery | Async tasks |
| Database | Stored state |

* * *

## Golden Rule

## 

Start with **audit logs**.

They tell you what actually happened, not what you think happened.

* * *

## Standard Debugging Flow

### 1\. Identify the Subject

## 

-   user\_id
-   request\_id
-   resource ID

* * *

### 2\. Check Audit Logs

## 

Look for:

-   recent actions
-   status transitions
-   actor identity
-   metadata

* * *

### 3\. Reconstruct the Timeline

## 

Example:

Request submitted  
    ↓  
Marked under review  
    ↓  
Approved  
    ↓  
Applied

If something is missing, that is your first clue.

* * *

### 4\. Verify Current State

## 

Check database:

- current status
- related objects
- timestamps

* * *

### 5\. Check Service Logic

## 

Validate:

- allowed transitions
- validation rules
- edge cases

* * *

### 6\. Check API Layer

## 

Verify:

- correct endpoint used
- request payload
- authentication context

* * *

### 7\. Check Async Tasks

## 

If involved:

- Celery worker logs
- retries
- failures

* * *

## Common Scenarios

## 

* * *

### Scenario 1: Profile Change Did Not Apply

#### Steps

## 

1.Check audit logs for `profile_update_applied`
2.If missing:
    - check if request was approved
    - verify apply endpoint was called
3.If present:
    - inspect `changes` field
    - verify profile data

* * *

### Scenario 2: Request Stuck in Pending

#### Steps

## 

1.Verify no reviewer action occurred
2.check audit logs for review events
3.confirm reviewer permissions
4.check if endpoint was triggered

* * *

### Scenario 3: User Reports Wrong Profile Data

#### Steps

## 

1.fetch audit logs for that user
2.find latest `profile_update_applied`
3.inspect field diffs
4.identify actor
5.confirm workflow sequence

* * *

### Scenario 4: Unauthorized Access

#### Steps

## 

1.check request.user
2.verify permissions logic
3.inspect tenant boundaries
4.confirm object ownership

* * *

### Scenario 5: Duplicate Requests Allowed

#### Steps

## 

1.check service validation logic
2.confirm query filters
3.verify transaction consistency
4.inspect race conditions

* * *

### Scenario 6: Audit Log Missing

#### Steps

## 

1.check Celery logs
2.check retry queue
3.verify `transaction.on_commit`
4.inspect service code
5.check for exceptions

* * *

## Debugging Tools

### Logs

## 

- application lo
- audit logs
- Celery logs

* * *

### Database

## 

- inspect records directly
- verify relationships
- check timestamps

* * *

### API Testing

## 

- Postman / curl
- reproduce requests manually

* * *

### Code Inspection

## 

- service layer logic
- permission checks
- serializers

* * *

## Reproducing Issues

## 

Always try to reproduce:

1.same user
2.same payload
3.same endpoint
4.same state

If it cannot be reproduced, investigate:

- race conditions
- async behavior
- environment differences

* * *

## Root Cause Analysis

## 

After fixing an issue, always ask:

- why did this happen?
- what assumption failed?
- what invariant was broken?

* * *

## Prevention Strategies

### 1\. Strengthen Validation

## 

- stricter input validation
- explicit checks in services

* * *

### 2\. Improve Audit Coverage

## 

- ensure all actions are logged
- add missing audit events

* * *

### 3\. Add Tests

## 

- edge cases
- invalid transitions
- permission boundaries

* * *

### 4\. Improve Observability

## 

- better logging
- metrics
- alerts

* * *

## Red Flags

## 

Watch out for:

- silent failures
- missing audit logs
- inconsistent states
- unexpected null values
- cross-tenant data

* * *

## Anti-Patterns

## 

Avoid:

- debugging from the UI only
- guessing root causes
- skipping audit logs
- patching without understanding
- fixing symptoms instead of causes

* * *

## Incident Response Workflow

### 1\. Identify Impact

## 

- how many users affected?
- which tenant?

* * *

### 2\. Contain

## 

- disable feature if needed
- prevent further damage

* * *

### 3\. Investigate

## 

- audit logs
- service logic
- system state

* * *

### 4\. Fix

## 

- correct code or data
- validate solution

* * *

### 5\. Verify

## 

- confirm issue resolved
- monitor for recurrence

* * *

### 6\. Document

## 

- root cause
- fix applied
- prevention steps

* * *

## Summary

## 

Debugging in this system relies on:

- audit logs as source of truth
- service layer as control point
- explicit workflows
- structured investigation

* * *

## Final Principle

## 

> If you cannot trace it, you cannot fix it.
