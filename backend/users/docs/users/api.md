# Users Domain API

## Purpose

This document defines the HTTP API surface for the users domain.

It covers:

- profile retrieval
- profile update request workflows
- request lifecycle actions
- permissions and expected responses

---

## Base Path

```text
/api/users/
```
## General API Principles

### 1\. Thin Views

## 

Views only:

-   validate request shape
-   delegate to services
-   return serialized responses

Business logic does not live in the API layer.

* * *

### 2\. Workflow Actions Are Explicit

## 

Profile updates are not done through direct `PATCH /profile/`.

Instead, they are modeled as explicit workflow actions:

-   submit
-   review
-   approve
-   reject
-   apply
-   cancel

* * *

### 3\. Authenticated Access Required

## 

All endpoints in this domain require authentication.

* * *

## Resources

### 1\. User

## 

Read-only identity resource.

### 2\. UserProfile

## 

Read-only approved profile resource.

### 3\. ProfileUpdateRequest

## 

Workflow resource for controlled profile mutation.

* * *

## Endpoints

## 

* * *

## Get Current User Profile

## 

Returns the current authenticated user’s approved profile.

### Request

## 

GET /api/users/profile/

### Response

## 

{  
  "id": 15,  
  "display\_name": "Jane Doe",  
  "name\_for\_display": "Jane Doe",  
  "bio": "Writer and editor.",  
  "avatar": "/media/users/avatars/15/avatar.png",  
  "timezone": "Africa/Nairobi",  
  "locale": "en",  
  "country": "Kenya",  
  "last\_seen\_at": "2026-03-30T09:00:00Z",  
  "created\_at": "2026-03-01T10:00:00Z",  
  "updated\_at": "2026-03-30T09:00:00Z"  
}

### Permissions

## 

-   Authenticated user only

* * *

## List Current User’s Profile Update Requests

## 

Returns all profile update requests belonging to the authenticated user.

### Request

## 

GET /api/users/profile-update-requests/

### Response

## 

\[  
  {  
    "id": 101,  
    "user": 15,  
    "profile": 15,  
    "website": 1,  
    "requested\_changes": {  
      "display\_name": "Jane A. Doe"  
    },  
    "status": "pending",  
    "submitted\_note": "Please update my display name.",  
    "reviewed\_by": null,  
    "reviewed\_at": null,  
    "review\_note": "",  
    "applied\_at": null,  
    "created\_at": "2026-03-30T10:00:00Z",  
    "updated\_at": "2026-03-30T10:00:00Z"  
  }  
\]

### Permissions

## 

-   Authenticated user only
-   Results must be scoped to the request owner

* * *

## Submit Profile Update Request

## 

Creates a new profile update request for the authenticated user.

### Request

## 

POST /api/users/profile-update-requests/  
Content-Type: application/json

### Request Body

## 

{  
  "requested\_changes": {  
    "display\_name": "Jane A. Doe",  
    "bio": "Updated professional bio."  
  },  
  "submitted\_note": "Updating public profile details."  
}

### Allowed Fields in `requested_changes`

## 

-   display\_name
-   bio
-   avatar
-   timezone
-   locale
-   country

### Response

## 

{  
  "id": 101,  
  "user": 15,  
  "profile": 15,  
  "website": 1,  
  "requested\_changes": {  
    "display\_name": "Jane A. Doe",  
    "bio": "Updated professional bio."  
  },  
  "status": "pending",  
  "submitted\_note": "Updating public profile details.",  
  "reviewed\_by": null,  
  "reviewed\_at": null,  
  "review\_note": "",  
  "applied\_at": null,  
  "created\_at": "2026-03-30T10:00:00Z",  
  "updated\_at": "2026-03-30T10:00:00Z"  
}

### Permissions

## 

-   Authenticated user
-   Role must be allowed to submit profile update requests
-   Tenant must be valid

### Validation Rules

## 

-   User must belong to a website
-   Only allowed fields may be present
-   Only one active request may exist at a time

### Audit Event

## 

profile\_update\_submitted

* * *

## Mark Request Under Review

## 

Marks a pending request as under review.

### Request

## 

POST /api/users/profile-update-requests/{id}/mark\_under\_review/

### Response

## 

{  
  "id": 101,  
  "status": "under\_review",  
  "reviewed\_by": 3,  
  "reviewed\_at": "2026-03-30T10:30:00Z"  
}

### Permissions

## 

-   Staff reviewer only
-   Must be authorized for the same tenant
-   Request must be in `PENDING`

### Audit Event

## 

profile\_update\_marked\_under\_review

* * *

## Approve Request

## 

Approves a pending or under-review request.

### Request

## 

POST /api/users/profile-update-requests/{id}/approve/  
Content-Type: application/json

### Request Body

## 

{  
  "review\_note": "Looks good."  
}

### Response

## 

{  
  "id": 101,  
  "status": "approved",  
  "reviewed\_by": 3,  
  "reviewed\_at": "2026-03-30T10:45:00Z",  
  "review\_note": "Looks good."  
}

### Permissions

## 

-   Staff reviewer only
-   Must be authorized for the same tenant

### Valid Source States

## 

-   `PENDING`
-   `UNDER_REVIEW`

### Audit Event

## 

profile\_update\_approved

* * *

## Reject Request

## 

Rejects a pending or under-review request.

### Request

## 

POST /api/users/profile-update-requests/{id}/reject/  
Content-Type: application/json

### Request Body

## 

{  
  "review\_note": "Submitted bio violates policy."  
}

### Response

## 

{  
  "id": 101,  
  "status": "rejected",  
  "reviewed\_by": 3,  
  "reviewed\_at": "2026-03-30T10:50:00Z",  
  "review\_note": "Submitted bio violates policy."  
}

### Permissions

## 

-   Staff reviewer only
-   Must be authorized for the same tenant

### Valid Source States

## 

-   `PENDING`
-   `UNDER_REVIEW`

### Validation Rules

## 

-   `review_note` is required

### Audit Event

## 

profile\_update\_rejected

* * *

## Cancel Request

## 

Cancels a pending or under-review request.

### Request

## 

POST /api/users/profile-update-requests/{id}/cancel/

### Response

## 

{  
  "id": 101,  
  "status": "cancelled"  
}

### Permissions

## 

-   Owner only

### Valid Source States

## 

-   `PENDING`
-   `UNDER_REVIEW`

### Audit Event

## 

profile\_update\_cancelled

* * *

## Apply Approved Request

## 

Applies the approved changes to the live `UserProfile`.

### Request

## 

POST /api/users/profile-update-requests/{id}/apply/

### Response

## 

{  
  "id": 101,  
  "status": "applied",  
  "applied\_at": "2026-03-30T11:00:00Z"  
}

### Permissions

## 

-   Staff reviewer or system-controlled flow
-   Must be authorized for the same tenant

### Valid Source State

## 

-   `APPROVED`

### Side Effects

## 

-   Updates `UserProfile`
-   Records field-level diffs
-   Marks request as `APPLIED`

### Audit Event

## 

profile\_update\_applied

* * *

## User Resource Endpoints

## 

These are read-oriented endpoints exposing identity data.

* * *

## Get User List

### Request

## 

GET /api/users/users/

### Notes

## 

This endpoint is typically read-only and should be tenant-scoped unless elevated staff access is intentionally supported.

### Response Example

## 

\[  
  {  
    "id": 15,  
    "email": "jane@example.com",  
    "username": "jane",  
    "role": "writer",  
    "phone\_number": "+254700000000",  
    "email\_verified": true,  
    "phone\_verified": false,  
    "full\_name": "Jane Doe",  
    "website": 1,  
    "is\_active": true,  
    "created\_at": "2026-03-01T10:00:00Z",  
    "updated\_at": "2026-03-30T09:00:00Z"  
  }  
\]

* * *

## Error Behavior

### Validation Error

## 

{  
  "review\_note": \[  
    "A rejection reason is required."  
  \]  
}

### Permission Denied

## 

{  
  "detail": "You do not have permission to perform this action."  
}

### Invalid Workflow State

## 

{  
  "detail": "Only approved requests can be applied."  
}

### Duplicate Active Request

## 

{  
  "detail": "You already have a pending profile update request."  
}

* * *

## Workflow State Summary

## 

| State | Meaning |
| --- | --- |
| pending | Request submitted |
| under\_review | Staff is reviewing |
| approved | Approved, waiting for application |
| rejected | Rejected by reviewer |
| cancelled | Cancelled by owner |
| applied | Applied to live profile |

* * *

## API Invariants

## 

The following must always hold:

1.  Profile updates are never applied directly through profile endpoints
2.  Only one active request exists per user
3.  Only valid workflow transitions are allowed
4.  All critical actions are audited
5.  All access is tenant-aware

* * *

## Anti-Patterns

## 

Avoid:

-   adding `PATCH /profile/` for direct mutation
-   approving and applying without service-layer validation
-   letting views mutate models directly
-   returning cross-tenant data

* * *

## Summary

## 

The Users API is intentionally workflow-driven, not CRUD-driven.

It is designed to ensure that:

-   profile mutation is controlled
-   requests are reviewable
-   state transitions are explicit
-   audit trails are preserved

* * *

## Final Principle

## 

> The API must expose safe workflows, not shortcuts.
