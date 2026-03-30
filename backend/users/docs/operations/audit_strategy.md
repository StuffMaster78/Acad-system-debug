# Audit Strategy (Operations)

## Purpose

This document defines how audit logging is handled in production.

It answers:

- how audit logs are written and stored
- how failures are handled
- how logs are queried and used operationally
- how the system scales audit data over time

This is an operations-level document.

For audit architecture and domain-level behavior, see:

- docs/architecture/audit_logging.md
- docs/users/audit.md

---

## Core Principle

> Audit logs must never block the system, but must never silently fail.

---

## Logging Flow (Production)

```text
Service Layer
    ↓
AuditLogService.log_auto(...)
    ↓
transaction.on_commit(...)
    ↓
Celery Task (async_log_audit)
    ↓
Database (AuditLogEntry)
```

## Why transaction.on\_commit Matters

### 

Audit logs must reflect committed state.

Without this:

-   logs may record actions that later roll back
-   audit becomes unreliable

Correct pattern:

DB transaction commits  
    ↓  
Audit log is dispatched

* * *

## Sync vs Async Logging

### Async Logging (Default)

### 

Used for:

-   most business events
-   high-frequency logs

Benefits:

-   non-blocking
-   scalable
-   retryable

* * *

### Sync Logging (Fallback)

### 

Used when:

-   async dispatch fails
-   system is in degraded mode
-   critical logging must not be delayed

* * *

## Failure Handling

### 1\. Async Task Failure

### 

Handled by Celery retry mechanism.

Typical configuration:

-   max\_retries: 3
-   retry delay: 5 seconds

* * *

### 2\. Actor Resolution Failure

### 

If user cannot be resolved:

-   log warning
-   proceed with actor = null

* * *

### 3\. Serialization Failure

### 

If payload is invalid:

-   sanitize or truncate payload
-   avoid crashing the task

* * *

### 4\. Database Failure

### 

If audit write fails:

-   log error
-   retry if async
-   do not block main workflow

* * *

## Observability

### 

Audit logging must be observable.

### Logs

### 

Use structured logging:

\[AUDIT\] Async log complete: action target(id)

* * *

### Metrics (Recommended)

### 

Track:

-   audit log success rate
-   audit log failure rate
-   retry counts
-   task queue latency

* * *

### Alerts (Recommended)

### 

Trigger alerts on:

-   repeated audit task failures
-   high retry rates
-   queue backlog

* * *

## Data Storage Strategy

### 

Audit logs grow continuously.

### Current

### 

-   stored in primary database
-   JSON metadata and changes

* * *

### Future

### 

Recommended strategies:

#### 1\. Partitioning

### 

Partition audit table by:

-   date (monthly or weekly)
-   tenant (optional)

* * *

#### 2\. Archiving

### 

Move old logs to:

-   cold storage
-   data warehouse
-   object storage

* * *

#### 3\. Retention Policies

### 

Define retention periods:

-   hot data: recent logs (e.g. 90 days)
-   cold data: archived logs

* * *

## Querying Audit Logs

### 

Common queries:

-   logs for a specific user
-   logs for a specific request
-   logs for a tenant
-   logs within time window
-   logs by action type

* * *

### Example Query Patterns

### 

Filter by action  
Filter by actor\_id  
Filter by target  
Filter by metadata.website\_id  
Filter by timestamp range

* * *

## Performance Considerations

### Payload Size

### 

-   metadata and changes should be bounded
-   avoid storing large blobs

* * *

### JSON Fields

### 

-   ensure indexing strategy supports queries
-   consider partial indexes on metadata fields

* * *

### Write Volume

### 

Audit logging may become one of the highest write volumes in the system.

Plan accordingly.

* * *

## Security Considerations

### 1\. Sensitive Data

### 

Never log:

-   passwords
-   tokens
-   secrets
-   OTP values

* * *

### 2\. Access Control

### 

Audit logs should not be freely accessible.

Restrict access to:

-   admins
-   authorized staff
-   internal tools

* * *

### 3\. Tamper Resistance

### 

Audit logs should be:

-   append-only
-   not editable through normal application flows

* * *

## Operational Playbooks

### Scenario: User Reports Unexpected Profile Change

### 

Steps:

1.  Identify user\_id
2.  Query audit logs
3.  Locate profile\_update\_applied event
4.  Inspect changes field
5.  Identify actor
6.  trace workflow events (submit → review → approve → apply)

* * *

### Scenario: Missing Audit Entry

### 

Steps:

1.  Check Celery logs
2.  Check retry queue
3.  verify transaction commit happened
4.  check application logs for failures

* * *

### Scenario: High Audit Failure Rate

### 

Steps:

1.  check Celery worker health
2.  check database connectivity
3.  inspect payload size
4.  check error logs
5.  scale workers if needed

* * *

## Integration with Other Systems

### Notifications

### 

Audit logs may trigger or correlate with notifications.

* * *

### Security Monitoring

### 

Audit logs may feed:

-   anomaly detection
-   fraud systems
-   login monitoring

* * *

### Analytics

### 

Audit logs can be used for:

-   user behavior analysis
-   workflow bottleneck detection
-   operational metrics

* * *

## Anti-Patterns

### 

Avoid:

-   synchronous logging everywhere
-   logging inside database transactions before commit
-   storing unbounded JSON data
-   ignoring audit failures
-   using audit logs as primary data store

* * *

## Testing Expectations

### 

Operational tests should verify:

-   async logging succeeds
-   retries work
-   fallback mechanisms exist
-   logs are written after commit

* * *

## Summary

### 

The audit strategy ensures:

-   reliability under failure
-   scalability under load
-   observability for debugging
-   traceability for compliance

* * *

## Final Principle

### 

> Audit logs must survive failure, scale with the system, and tell the truth about what actually happened.
