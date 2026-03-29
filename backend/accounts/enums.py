from django.db import models


class AccountStatus(models.TextChoices):
    """Lifecycle status for an account profile."""

    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    DISABLED = "disabled", "Disabled"
    UNDER_REVIEW = "under_review", "Under Review"


class OnboardingStatus(models.TextChoices):
    """Onboarding progress for an account profile."""

    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    EXPIRED = "expired", "Expired"


class ReservedRoleKey(models.TextChoices):
    """Reserved built in role keys for the platform."""

    SUPER_ADMIN = "super_admin", "Super Admin"
    ADMIN = "admin", "Admin"
    EDITOR = "editor", "Editor"
    SUPPORT = "support", "Support"
    WRITER = "writer", "Writer"
    CLIENT = "client", "Client"


class AccountAuditEventType(models.TextChoices):
    """Audit events for account lifecycle changes."""

    ACCOUNT_CREATED = "account_created", "Account Created"
    ACCOUNT_ACTIVATED = "account_activated", "Account Activated"
    ACCOUNT_SUSPENDED = "account_suspended", "Account Suspended"
    ACCOUNT_REACTIVATED = "account_reactivated", "Account Reactivated"
    ROLE_ASSIGNED = "role_assigned", "Role Assigned"
    ROLE_REVOKED = "role_revoked", "Role Revoked"
    CLIENT_ONBOARDING_COMPLETED = (
        "client_onboarding_completed",
        "Client Onboarding Completed",
    )
    WRITER_ONBOARDING_COMPLETED = (
        "writer_onboarding_completed",
        "Writer Onboarding Completed",
    )
    STAFF_ONBOARDING_COMPLETED = (
        "staff_onboarding_completed",
        "Staff Onboarding Completed",
    )


class OnboardingType(models.TextChoices):
    """Supported onboarding flows."""

    CLIENT = "client", "Client"
    WRITER = "writer", "Writer"
    STAFF = "staff", "Staff"