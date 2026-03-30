# API Conventions

## Purpose

This document defines global API conventions used across the system.

It ensures:

- consistency across endpoints
- predictable request/response behavior
- easier frontend integration
- simpler debugging and maintenance

---

## Scope

These conventions apply to all APIs, including:

- users
- accounts
- authentication
- payments (future)
- notifications (future)

---

## Core Principles

### 1. Consistency Over Cleverness

All endpoints should behave predictably.

Do not invent new patterns per endpoint.

---

### 2. Explicit Over Implicit

- Actions should be clear
- Responses should be structured
- Errors should be descriptive

---

### 3. Workflow-Driven APIs

Where applicable, APIs should expose workflows, not raw CRUD.

Example:

Bad:

```text
PATCH /profile/
```
### 

Good:

POST /profile-update-requests/  
POST /profile-update-requests/{id}/approve/

* * *

## Base URL Structure

### 

/api/{domain}/{resource}/

Examples:

/api/users/profile/  
/api/users/profile-update-requests/  
/api/accounts/roles/

* * *

## HTTP Methods

### 

| Method | Usage |
| --- | --- |
| GET | Retrieve data |
| POST | Create or trigger actions |
| PUT | Replace full resource (rare) |
| PATCH | Partial update (avoid for workflow-controlled resources) |
| DELETE | Remove resource |

* * *

## Action Endpoints

### 

For workflows, use action endpoints:

POST /resource/{id}/action\_name/

Examples:

POST /profile-update-requests/{id}/approve/  
POST /profile-update-requests/{id}/reject/  
POST /profile-update-requests/{id}/apply/

* * *

## Request Format

### Content Type

### 

Content-Type: application/json

* * *

### JSON Body

### 

All request bodies must be valid JSON.

* * *

## Response Format

### Success Response

### 

Standard structure:

{  
  "data": { ... }  
}

or for list endpoints:

{  
  "data": \[ ... \]  
}

* * *

### Alternative (Allowed)

### 

Direct object return is acceptable for DRF-style APIs:

{  
  "id": 1,  
  "name": "Example"  
}

But consistency within a domain is required.

* * *

## Status Codes

### 

| Code | Meaning |
| --- | --- |
| 200 | Success |
| 201 | Resource created |
| 204 | No content |
| 400 | Validation error |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Not found |
| 409 | Conflict |
| 500 | Internal server error |

* * *

## Error Handling

### Standard Error Format

### 

{  
  "detail": "Error message"  
}

* * *

### Field-Level Errors

### 

{  
  "field\_name": \[  
    "Error message"  
  \]  
}

* * *

### Multiple Errors

### 

{  
  "field1": \["Error 1"\],  
  "field2": \["Error 2"\]  
}

* * *

## Authentication

### 

All protected endpoints require authentication.

Typical pattern:

Authorization: Bearer <token>

(Exact implementation defined in `api/authentication.md`)

* * *

## Pagination

### 

List endpoints should support pagination.

### Standard Format

### 

```json
{  
  "count": 100,  
  "next": "...",  
  "previous": "...",  
  "results": \[ ... \]  
}
```

* * *

## Filtering

### 

Filtering should be supported via query parameters.

Example:

GET /profile-update-requests/?status=pending

* * *

## Ordering

### 

Ordering via query params:

GET /profile-update-requests/?ordering=-created\_at

* * *

## Naming Conventions

### URLs

### 

-   lowercase
-   kebab-case
-   plural nouns

Example:

/profile-update-requests/

* * *

### Fields

### 

-   snake\_case

Example:

{  
  "display\_name": "Jane"  
}

* * *

## Idempotency

### Safe Operations

### 

- GET → always safe
- POST → not guaranteed safe unless explicitly designed

* * *

### Idempotent Design (Future)

### 

Critical operations (like payments) should support idempotency keys.

* * *

## Tenant Awareness

### 

All APIs must respect tenant boundaries.

Implicit:

request.user.website

Explicit filters may be applied where necessary.

* * *

## Versioning (Future)

### 

Recommended approach:

/api/v1/...

* * *

## Security Considerations

### 

- Never expose sensitive fields
- Validate all inputs
- Do not trust client-provided identifiers blindly
- Enforce permissions at API and service layers

* * *

## Anti-Patterns

### 

Avoid:

- inconsistent response formats
- mixing business logic into views
- exposing internal model structure unnecessarily
- skipping validation for "trusted" clients
- returning raw exceptions

* * *

## Testing Expectations

### 

APIs should be tested for:

- valid requests
- invalid input
- permission enforcement
- tenant isolation
- correct status codes

* * *

## Summary

### 

The API layer must be:

- predictable
- consistent
- secure
- workflow-aware

* * *

## Final Principle

### 

> An API is a contract.  
> If it surprises the client, it is broken.