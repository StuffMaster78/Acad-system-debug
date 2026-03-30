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

## 

Each layer must independently enforce constraints.

* * *

## Identity and Access Control

### Authentication

## 

-   All protected endpoints require authentication
-   Identity is derived from credentials, not request payload
-   Inactive users must not be allowed access

* * *

### Authorization

## 

-   Role-based access via accounts domain
-   Object-level permission checks
-   Tenant-aware enforcement

* * *

### Principle of Least Privilege

## 

Users and services should have:

-   only the access they need
-   no implicit elevation
-   no hidden bypass paths

* * *

## Multi-Tenancy Isolation

## 

Tenant boundaries must be strictly enforced.

### Rule

## 

request.user.website must match object.website

* * *

### Risks if Broken

## 

-   data leakage
-   cross-tenant access
-   privacy violations

* * *

## Input Validation

## 

All inputs must be validated at:

-   serializer level (structure)
-   service layer (business rules)

* * *

### Never Trust Client Input

## 

Bad:

{  
  "user\_id": 10  
}

Good:

-   derive user from authentication
-   validate all fields explicitly

* * *

## Sensitive Data Handling

### Never Store or Log

## 

-   passwords
-   tokens
-   secrets
-   OTP codes
-   private keys

* * *

### Audit Logging Constraints

## 

Audit logs must:

-   redact sensitive values
-   store only necessary context
-   avoid exposing secrets in metadata

* * *

## API Security

### Required Practices

## 

-   enforce authentication on protected endpoints
-   return correct HTTP status codes
-   avoid leaking internal errors
-   validate all request bodies

* * *

### Rate Limiting (Recommended)

## 

Protect endpoints from abuse:

-   login endpoints
-   sensitive workflows
-   public APIs

* * *

## Session and Token Security

## 

The system should enforce:

-   expiration of credentials
-   revocation support
-   detection of suspicious activity

* * *

### Future Enhancements

## 

- MFA enforcement
- device tracking
- session invalidation
- login alerts

* * *

## Password Security

## 

Passwords must:

- be hashed (never stored in plain text)
- use strong hashing algorithms
- never be logged or exposed

* * *

## Transport Security

## 

All API communication must occur over:

HTTPS

Never allow plaintext transmission in production.

* * *

## Data Access Control

### Database Access

## 

- restrict direct database access
- use application-layer validation
- enforce role-based access in services

* * *

### Internal Tools

## 

Admin tools must:

-   enforce authentication
-   log actions
-   restrict sensitive operations

* * *

## Audit Logging and Security

## 

Audit logs are part of the security model.

They enable:

-   incident investigation
-   fraud detection
-   accountability

* * *

### Requirements

## 

-   all sensitive actions must be logged
-   logs must be immutable
-   logs must include actor and context

* * *

## Failure Handling

## 

Security failures must be:

-   explicit
-   logged
-   observable

* * *

### Examples

## 

| Failure | Response |
| --- | --- |
| Invalid auth | 401 |
| Unauthorized action | 403 |
| Invalid input | 400 |
| Suspicious activity | log + alert |

* * *

## Common Threats

### 1\. Unauthorized Access

## 

Mitigation:

-   authentication
-   permission checks
-   tenant validation

* * *

### 2\. Data Leakage

## 

Mitigation:

-   tenant isolation
-   filtered queries
-   response sanitization

* * *

### 3\. Injection Attacks

## 

Mitigation:

-   ORM usage
-   input validation
-   avoiding raw queries

* * *

### 4\. Replay Attacks (Future)

## 

Mitigation:

-   token expiration
-   idempotency keys
-   request validation

* * *

### 5\. Credential Theft

## 

Mitigation:

-   HTTPS
-   secure storage
-   short-lived tokens

* * *

## Operational Monitoring

## 

Security must be observable.

### Logs

## 

Monitor:

-   login attempts
-   failed authentication
-   permission denials
-   unusual activity patterns

* * *

### Alerts

## 

Trigger alerts for:

-   repeated failed logins
-   unusual request volume
-   suspicious account behavior

* * *

## Incident Response

### Example: Suspicious Profile Change

## 

Steps:

1.  identify user
2.  check audit logs
3.  verify actor and workflow
4.  revert if necessary
5.  notify affected user

* * *

### Example: Unauthorized Access Attempt

## 

Steps:

1.  inspect logs
2.  identify source IP
3.  verify credentials used
4.  revoke sessions if needed
5.  escalate if pattern persists

* * *

## Anti-Patterns

## 

Avoid:

-   trusting frontend validation
-   exposing internal errors
-   skipping permission checks
-   hardcoding roles in views
-   mixing authentication and authorization logic

* * *

## Testing Expectations

## 

Security testing should cover:

-   authentication enforcement
-   permission boundaries
-   tenant isolation
-   invalid input handling
-   edge cases in workflows

* * *

## Summary

## 

The system enforces security through:

-   layered validation
-   strict access control
-   tenant isolation
-   audit logging
-   operational monitoring

* * *

## Final Principle

## 

> Security is not about blocking attacks.  
> It is about making unsafe states impossible.
