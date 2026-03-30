# Audit Logging Architecture

## Purpose

The audit logging system provides a reliable, structured, and tamper-resistant record of all critical system actions.

It exists to ensure:

- Traceability
- Debuggability
- Accountability
- Compliance readiness

---

## Core Principle

> If an action matters, it must be auditable.

---

## Responsibilities

The audit logging system tracks:

- State transitions
- Data mutations
- Security-related actions
- System events

---

## Architecture

```text
Service Layer
    ↓
AuditLogService
    ↓
Payload Normalization
    ↓
Async Dispatch (Celery)
    ↓
Database (AuditLogEntry)

## Components

### 1\. AuditLogService

## 

Central entry point for all audit logging.

#### Responsibilities

## 

-   Normalize payload
-   Sanitize sensitive data
-   Attach metadata (IP, user agent, request ID)
-   Dispatch async or sync logging

* * *

### 2\. Async Task (Celery)

## 

Handles persistence asynchronously.

#### Responsibilities

## 

-   Write to database
-   Retry on failure
-   Avoid blocking request lifecycle

* * *

### 3\. AuditLogEntry Model

## 

Represents a single audit record.

* * *

## AuditLogEntry Fields

## 

| Field | Description |
| --- | --- |
| action | Type of event |
| actor\_id | User who performed action |
| target | Affected entity (app.Model) |
| target\_id | ID of affected object |
| metadata | Additional context |
| changes | Field-level diffs |
| ip\_address | Client IP |
| user\_agent | Client device |
| notes | Optional explanation |
| request\_id | Request correlation ID |
| timestamp | Event time |
| target\_content\_type\_id | Django content type |
| target\_object\_id | Generic FK reference |

* * *

## Payload Structure

### Example

## 

{  
  "action": "profile\_update\_applied",  
  "actor\_id": 10,  
  "target": "users.UserProfile",  
  "target\_id": 55,  
  "changes": {  
    "display\_name": {  
      "from": "Old Name",  
      "to": "New Name"  
    },  
    "\_\_request\_status\_\_": {  
      "from": "approved",  
      "to": "applied"  
    }  
  },  
  "metadata": {  
    "website\_id": 1,  
    "subject\_user\_id": 20  
  }  
}

* * *

## Logging Flow

### 1\. Service triggers audit

## 

AuditLogService.log\_auto(...)

* * *

### 2\. Payload normalized

## 

-   Actor resolved
-   Target normalized
-   Metadata sanitized
-   Changes truncated if needed

* * *

### 3\. Async dispatch

## 

transaction.on\_commit(...)

Ensures logs are only created after DB commit.

* * *

### 4\. Celery task persists log

## 

async\_log\_audit(...)

* * *

## Sync vs Async Logging

## 

| Mode | Use Case |
| --- | --- |
| Async | Default |
| Sync | Critical fallback |

* * *

## Security Considerations

### Sensitive Data Filtering

## 

The system automatically redacts:

-   passwords
-   tokens
-   secrets
-   API keys
-   OTPs

* * *

### Data Integrity

## 

-   Logs are append-only
-   No mutation allowed
-   No deletion in normal operation

* * *

## Performance Considerations

## 

-   JSON payloads truncated if too large
-   Async processing reduces request latency
-   Logging must not block user actions

* * *

## Failure Handling

## 

| Scenario | Behavior |
| --- | --- |
| Async failure | Retry |
| Sync failure | Logged, does not break flow |
| Serialization error | Payload truncated |

* * *

## Audit Events (Users Example)

## 

| Event | Description |
| --- | --- |
| profile\_update\_submitted | Request created |
| profile\_update\_marked\_under\_review | Review started |
| profile\_update\_approved | Approved |
| profile\_update\_rejected | Rejected |
| profile\_update\_cancelled | Cancelled |
| profile\_update\_applied | Changes applied |

* * *

## Design Decisions

### Why async logging?

## 

-   Avoid blocking user requests
-   Improve performance

* * *

### Why normalize payload?

## 

-   Consistency between sync and async
-   Easier querying and analysis

* * *

### Why store changes?

## 

-   Enables reconstruction of events
-   Supports debugging and compliance

* * *

## Future Enhancements

## 

-   Log retention policies
-   Partitioned audit tables
-   External log streaming (Kafka)
-   Search indexing (Elasticsearch)

* * *

## Anti-Patterns

## 

Avoid:

-   Logging directly from views
-   Logging without normalization
-   Storing raw sensitive data
-   Skipping audit for critical actions

* * *

## Summary

## 

The audit system guarantees:

-   Every important action is recorded
-   Data changes are traceable
-   Logs are consistent and structured

* * *

## Final Principle

## 

> If you cannot reconstruct what happened, your system is already unreliable.
