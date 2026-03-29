# Accounts Services

## Purpose

Services contain ALL business logic.

---

## Core Services

### AccountCreationService

- Creates account profiles

### AccountRoleService

- Assign roles
- Revoke roles

### AccountActivationService

- Activate account
- Suspend account
- Reactivate account

### ClientOnboardingService

- Assign client role
- Mark onboarding complete

### WriterOnboardingService

- Assign writer role
- Handle review logic

### StaffOnboardingService

- Assign staff roles

---

## Rules

- Services can call other services
- Services can call selectors
- Services must NOT depend on views
