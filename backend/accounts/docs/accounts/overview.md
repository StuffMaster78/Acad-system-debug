# Accounts System Overview

The `accounts` app is the source of truth for:

- Account membership within a website
- Role assignment and role lifecycle
- Account lifecycle (activation, suspension, etc)
- Onboarding workflows (client, writer, staff)
- Account-level audit logging

## What it does NOT handle

- Authentication (handled by `authentication`)
- Identity (handled by `users`)
- Payments (handled by `payments_processor`)
- Notifications (handled by `notifications_system`)

## Core Idea

A `User` is identity.

An `AccountProfile` is:
> "This user, on this website, with these roles and lifecycle state."

This allows:

- multi-tenant support
- multi-role support
- clean separation of concerns
