# Multi-Tenancy Architecture

## Purpose

This document defines how multi-tenancy is implemented and enforced across the system.

Multi-tenancy ensures that:

- Data is isolated per tenant
- Users cannot access data outside their tenant
- System behavior is scoped and predictable

---

## Core Concept

The system uses a **shared database, tenant-scoped model**.

Each user belongs to a tenant:

```text
User → belongs to → Website (tenant)

Tenant Model
------------

### Website

Represents a tenant in the system.

#### Responsibilities

*   Owns users
    
*   Owns data
    
*   Defines operational scope
    

Tenant Ownership
----------------

All tenant-scoped models must include:

`   website → ForeignKey   `

Example
-------

`   User  └── websiteUserProfile  └── user → websiteProfileUpdateRequest  └── user → website   `

Enforcement Rules
-----------------

### 1\. Every request must be tenant-aware

All operations must ensure:

`   request.user.website == object.website   `

### 2\. No cross-tenant access

This must always be prevented:

`   User A (Website X) accessing data from Website Y   `

### 3\. Queries must be scoped

Bad:

`   User.objects.all()   `

Good:

`   User.objects.filter(website=request.user.website)   `

### 4\. Services enforce tenant rules

Tenant validation should happen in:

*   Services
    
*   Permissions layer
    

Not only in views.

API-Level Enforcement
---------------------

All endpoints must:

*   Use request.user.website
    
*   Filter queryset by tenant
    
*   Validate object ownership
    

Example
-------

`   if request_obj.website != request.user.website:    raise PermissionDenied("Cross-tenant access denied")   `

Model-Level Design
------------------

### Preferred Pattern

`   class SomeModel(models.Model):    website = models.ForeignKey("websites.Website", on_delete=models.CASCADE)   `

### Indirect Ownership

If a model does not have website directly:

*   It must be reachable via a chain:
    

`   Model → User → Website   `

Why This Design
---------------

### Simplicity

*   Single database
    
*   No schema duplication
    

### Performance

*   Easier indexing
    
*   Simpler queries
    

### Flexibility

*   Easy to scale later
    
*   Supports per-tenant features
    

Failure Scenarios
-----------------

ScenarioRiskPreventionMissing filterData leakAlways filter by websiteWrong joinsCross-tenant accessValidate ownershipBackground tasksUnsafe accessPass tenant context explicitly

Background Tasks (Important)
----------------------------

Celery tasks must be tenant-aware.

Never assume context.

Bad:

`   process_request(request_id)   `

Good:

`   process_request(request_id, website_id)   `

Audit Logging + Tenancy
-----------------------

Audit logs must include tenant context:

`   {  "metadata": {    "website_id": 1  }}   `

This ensures traceability per tenant.

Future Extensions
-----------------

### 1\. Database-Level Isolation

*   Separate schemas per tenant
    
*   Row-level security
    

### 2\. Tenant-Specific Config

*   Feature flags
    
*   Branding
    
*   Rate limits
    

### 3\. Subdomain Routing

`   tenant.example.com   `

Anti-Patterns
-------------

Avoid:

*   Global queries without filters
    
*   Hardcoded tenant IDs
    
*   Cross-tenant joins without validation
    
*   Trusting frontend for tenant enforcement
    

Summary
-------

Multi-tenancy is enforced through:

*   Explicit relationships
    
*   Query filtering
    
*   Service-level validation
    
*   API-level checks
    

Final Rule
----------

> If tenant boundaries are broken, the system is compromised.
