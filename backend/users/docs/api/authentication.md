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

{  
  "count": 100,  
  "next": "...",  
  "previous": "...",  
  "results": \[ ... \]  
}

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

-   GET → always safe
-   POST → not guaranteed safe unless explicitly designed

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

-   Never expose sensitive fields
-   Validate all inputs
-   Do not trust client-provided identifiers blindly
-   Enforce permissions at API and service layers

* * *

## Anti-Patterns

### 

Avoid:

-   inconsistent response formats
-   mixing business logic into views
-   exposing internal model structure unnecessarily
-   skipping validation for "trusted" clients
-   returning raw exceptions

* * *

## Testing Expectations

### 

APIs should be tested for:

-   valid requests
-   invalid input
-   permission enforcement
-   tenant isolation
-   correct status codes

* * *

## Summary

### 

The API layer must be:

-   predictable
-   consistent
-   secure
-   workflow-aware

* * *

## Final Principle

### 

> An API is a contract.  
> If it surprises the client, it is broken.

### 

This is the expected client contract unless an alternative authentication mechanism is explicitly documented.

* * *

## Request Example

### 

GET /api/users/profile/  
Authorization: Bearer eyJhbGciOi...

* * *

## Authentication Flow

### 

The exact implementation may vary, but the general flow is:

Client sends credentials  
    ↓  
Authentication system validates credentials  
    ↓  
Authenticated user is resolved  
    ↓  
Request proceeds to permission checks

* * *

## Request Lifecycle

### 

For a protected endpoint, request handling should proceed as follows:

Request  
    ↓  
Authentication  
    ↓  
Authenticated user resolved  
    ↓  
Permission checks  
    ↓  
Service layer validation  
    ↓  
Response

This order matters.

A request must not reach sensitive business logic before authentication is complete.

* * *

## Authenticated Request Contract

### 

A valid authenticated request must provide:

-   a valid authentication token or session credential
-   a credential that maps to an active user
-   credentials that have not expired or been revoked

* * *

## Failure Cases

### 

Authentication can fail for several reasons.

### Missing Credentials

### 

The client did not send any authentication data.

Example response:

{  
  "detail": "Authentication credentials were not provided."  
}

Expected status:

401 Unauthorized

* * *

### Invalid Credentials

### 

The provided token or session is invalid.

Example response:

{  
  "detail": "Invalid authentication credentials."  
}

Expected status:

401 Unauthorized

* * *

### Expired Credentials

### 

The credential is structurally valid but expired.

Example response:

{  
  "detail": "Authentication token has expired."  
}

Expected status:

401 Unauthorized

* * *

### Revoked or Disabled Access

### 

The user exists, but access is no longer valid.

Examples:

-   user deactivated
-   session revoked
-   token blacklisted

Example response:

{  
  "detail": "Authentication is no longer valid for this account."  
}

Expected status:

401 Unauthorized

* * *

## Authentication vs Permission Denial

### 

This distinction must remain clear.

### Authentication Failure

### 

The system could not verify who the client is.

Response:

401 Unauthorized

* * *

### Permission Failure

### 

The system knows who the client is, but the client is not allowed to perform the action.

Response:

403 Forbidden

* * *

## Session and Token Expectations

### 

Regardless of implementation style, the API authentication system should eventually support:

-   credential expiration
-   revocation
-   active user validation
-   audit logging of security events

* * *

## Recommended Security Rules

### 1\. Never Trust Client Identity Directly

### 

The client must never be allowed to declare its own user identity in request payloads.

Bad:

{  
  "user\_id": 15  
}

for actions that should derive the user from authentication.

Good:

-   derive the acting user from the authentication layer
-   use `request.user`

* * *

### 2\. Protect All Sensitive Endpoints

### 

All endpoints that expose or mutate user-owned or tenant-owned data must require authentication.

* * *

### 3\. Re-check Active User State

### 

Authentication should not only validate the token.

It should also ensure:

-   user is active
-   access is not revoked
-   session is still valid

* * *

### 4\. Treat Authentication as Security Infrastructure

### 

Authentication must be:

-   explicit
-   centralized
-   testable
-   auditable

Do not scatter ad hoc authentication logic across views.

* * *

## Tenant Awareness

### 

Authentication identifies the user.

Tenant enforcement happens after identity resolution.

Typical flow:

Authentication resolves request.user  
    ↓  
System derives request.user.website  
    ↓  
Permissions and services enforce tenant boundaries

Authentication alone does not guarantee tenant-safe access.  
It only establishes identity.

* * *

## Current and Future Mechanisms

### Current

### 

The API should use a single consistent authentication mechanism for protected endpoints.

Typical options include:

-   bearer token authentication
-   session authentication
-   JWT-based auth

Only one should be treated as the primary contract unless explicitly documented otherwise.

* * *

### Future

### 

The authentication system is expected to grow to support:

-   MFA
-   session tracking
-   device trust
-   login alerts
-   lockout rules
-   impersonation safeguards

These features belong to the authentication domain, not the users domain.

* * *

## MFA Direction

### 

Multi-factor authentication should be treated as a second stage of identity verification.

Typical future flow:

Primary credentials  
    ↓  
MFA challenge  
    ↓  
Authenticated session issued

This should remain transparent to protected APIs once authentication is complete.

Protected APIs should not need to know the MFA internals. They only need to trust the resulting authenticated identity.

* * *

## Session and Token Revocation

### 

The system should eventually support explicit invalidation of credentials.

Examples:

-   logout invalidates current session
-   admin revokes session
-   suspicious login forces reauthentication
-   password reset invalidates existing sessions

* * *

## Audit Expectations

### 

Authentication events should be auditable.

Important authentication-related events include:

-   login success
-   login failure
-   logout
-   session revoked
-   MFA enabled/disabled
-   suspicious login detected
-   lockout triggered

These do not belong in the users domain documentation, but they are part of the broader authentication contract.

* * *

## API Consumer Guidance

### 

Clients integrating with the API should follow these rules:

### 1\. Always send credentials on protected endpoints

### 2\. Never cache credentials insecurely

### 3\. Handle 401 and 403 differently

### 

- `401` means re-authentication may be needed
- `403` means the client is authenticated but not allowed

### 4\. Do not assume token permanence

### 

Tokens and sessions may expire or be revoked.

* * *

## Testing Expectations

### 

Authentication behavior should be tested for:

- missing credentials
- invalid credentials
- expired credentials
- revoked access
- active user checks
- correct 401 vs 403 behavior

* * *

## Anti-Patterns

### 

Avoid:

- mixing authentication and permission logic
- trusting user IDs in request bodies for authenticated actions
- implementing per-view custom auth hacks
- returning inconsistent auth failure responses
- allowing inactive users through valid tokens

* * *

## Summary

### 

API authentication is responsible for establishing a trusted acting identity for every protected request.

It must be:

- consistent
- secure
- centralized
- auditable

* * *

## Final Principle

### 

> The API should never ask the client who it is.
> The API should verify that independently.
