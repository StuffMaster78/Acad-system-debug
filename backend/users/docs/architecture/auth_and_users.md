# Authentication and Users Architecture

## Purpose

This document defines the separation between:

- Identity (`users`)
- Authentication (`authentication`)
- Authorization (`accounts`)

This separation is intentional and critical for system scalability and maintainability.

---

## Core Separation

| Concern | Domain |

|--------|------|
| Identity | users |
| Authentication | authentication |
| Authorization | accounts |

---

## 1. Users Domain (Identity)

The `users` domain is responsible for:

- Who the user is
- Basic identity data
- Profile information

### Responsibilities

- User model
- UserProfile
- Profile update workflows
- Tenant association (website)

---

### What Users SHOULD NOT handle

- Login logic
- Sessions
- MFA
- Permissions/roles logic

---

## 2. Authentication Domain

The `authentication` domain handles:

- Login / logout
- Sessions / tokens
- MFA (future)
- Account lockout
- Device tracking
- Login alerts

---

### Example Flow

```bash
User submits credentials
    ↓
Authentication validates
    ↓
Session/token created
    ↓
User authenticated
```

## 3\. Accounts Domain (Authorization)

The `accounts` domain handles:

- Roles
- Permissions
- Access control

### Example

User → has role → determines access

## Why This Separation Matters

### 1\. Avoid Role Explosion in User Model

Bad:

user.is\_writer  
user.is\_admin  
user.is\_editor

Good:

User → Role → Permissions

### 2\. Flexibility

You can:

- Change authentication strategy
- Add MFA
- Introduce SSO

Without touching the User model.

### 3\. Security

Authentication concerns are isolated and hardened.

### 4\. Scalability

Each domain can evolve independently.

## Data Flow

Client → Authentication → User → Accounts → Permissions

## Example Request Flow

### Accessing a Protected Resource

Request  
  ↓  
Authentication → validates session  
  ↓  
User resolved  
  ↓  
Accounts → checks permissions  
  ↓  
Access granted/denied

## Integration Points

### Users ↔ Authentication

- Authentication resolves a `User`
- Users do not manage sessions

### Users ↔ Accounts

- Users have roles
- Accounts define permissions

### Authentication ↔ Audit Logging

- Login events are audited
- Security actions are tracked

## Future Extensions

### Authentication

- MFA (OTP, TOTP)
- Session management
- Device tracking
- Login alerts
- Impersonation

### Users

- Profile versioning
- Privacy controls
- Data export

### Accounts

- Fine-grained permissions
- Feature flags
- Role hierarchies

## Anti-Patterns

Avoid:

- Putting authentication logic in User model
- Storing roles directly on User
- Mixing login logic with profile logic
- Hardcoding permissions

## Summary

| Domain | Responsibility |
| --- | --- |
| Users | Identity |
| Authentication | Login & security |
| Accounts | Access control |

## Final Principle

> Users represent identity, not behavior.
> Authentication verifies identity.
> Accounts determine what identity can do.
