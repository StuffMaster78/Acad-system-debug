"""
Core enums for writer management.

These represent fixed system states only.
They are NOT configurable by admins.
They are NOT financial rules.
They are NOT level definitions.

If it changes often, it does NOT belong here.
"""

from django.db import models


class WriterStatus(models.TextChoices):
    """
    Platform governance state of a writer.

    This controls whether a writer is allowed
    to participate in the system at all.
    """

    ACTIVE = "active", "Active"
    UNDER_REVIEW = "under_review", "Under Review"
    RESTRICTED = "restricted", "Restricted"
    SUSPENDED = "suspended", "Suspended"
    DEACTIVATED = "deactivated", "Deactivated"


class WriterOnlineStatus(models.TextChoices):
    """
    Real-time availability state.

    Used for live assignment and dashboard presence.
    Has NO effect on assignment routing.
    Routing gates live on WriterCapacity (can_take_orders,
    is_accepting_orders) and WriterAvailabilityWindow.
    """

    ONLINE = "online", "Online"
    OFFLINE = "offline", "Offline"
    AWAY = "away", "Away"
    BUSY = "busy", "Busy"

class WriterCapacityState(models.TextChoices):
    """
    Runtime workload pressure state.
    """

    AVAILABLE = "available", "Available"
    BUSY = "busy", "Busy"
    FULL = "full", "Full"
    OVERLOADED = "overloaded", "Overloaded"


class WriterDisciplineState(models.TextChoices):
    """
    Compliance and behavioral state.

    Lightweight enforcement signals only.
    """

    CLEAN = "clean", "Clean"
    WARNED = "warned", "Warned"
    RESTRICTED = "restricted", "Restricted"
    FINAL_WARNING = "final_warning", "Final Warning"
    BLACKLISTED = "blacklisted", "Blacklisted"


class WriterPenNameStatus(models.TextChoices):
    """
    Approval lifecycle for writer aliases.
    """

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    DISABLED = "disabled", "Disabled"


class WriterVerificationStatus(models.TextChoices):
    """
    Trust verification state.
    is_verified=True is only set when status=VERIFIED.
    Enforced by WriterDisciplineState CheckConstraint
    """

    UNVERIFIED = "unverified", "Unverified"
    PENDING = "pending", "Pending"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"


class WriterOnboardingStatus(models.TextChoices):
    """
    Writer-domain onboarding progress. Stored on WriterProfile.
 
    Separate from accounts.OnboardingStatus which tracks
    platform-level setup (role, portal, tenant access).
 
    These states track writer-specific requirements:
    document submission, qualification review, level assignment.
 
    Transitions (enforced by WriterProfileService):
        NOT_STARTED       → IN_PROGRESS         (profile created)
        IN_PROGRESS       → DOCUMENTS_PENDING   (writer submits docs)
        DOCUMENTS_PENDING → REVIEW_PENDING      (admin accepts docs)
        DOCUMENTS_PENDING → REJECTED            (admin rejects docs)
        REVIEW_PENDING    → COMPLETED           (admin final approval)
        REVIEW_PENDING    → REJECTED            (admin rejects at final review)
        REJECTED          → IN_PROGRESS         (writer corrects and resubmits)
    """

    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    DOCUMENTS_PENDING = "documents_pending", "Documents Pending"
    REVIEW_PENDING = "review_pending", "Review Pending"
    REJECTED = "rejected", "Rejected"
    COMPLETED = "completed", "Completed"


class WriterAssignmentEligibility(models.TextChoices):
    """
    Output states of eligibility evaluation.

    This is NOT stored as source of truth.
    It is a computed result for routing decisions.
    """

    ELIGIBLE = "eligible", "Eligible"
    INELIGIBLE = "ineligible", "Ineligible"
    OFFLINE = "offline", "Offline"
    AT_CAPACITY = "at_capacity", "At Capacity"
    RESTRICTED = "restricted", "Restricted"
    SUSPENDED = "suspended", "Suspended"
    UNVERIFIED = "unverified", "Unverified"
    ONBOARDING_INCOMPLETE = (
        "onboarding_incomplete",
        "Onboarding Incomplete",
    )


class DisciplineChangeType(models.TextChoices):
    STRIKE = "strike", "Strike"
    SUSPENSION = "suspension", "Suspension"
    BLACKLIST = "blacklist", "Blacklist"
    PROBATION = "probation", "Probation"
    PENALTY = "penalty", "Penalty"
    LIFT = "lift", "Lifted"


class LevelChangeType(models.TextChoices):
    """
    Nature of a writer level change. Stored on WriterLevelChangeLog.
    """  
    PROMOTION = "promotion", "Promotion"
    DEMOTION = "demotion", "Demotion"
    MANUAL = "manual", "Manual Override"
    INITIAL = "initial", "Initial Assignment"


class LevelChangeTrigger(models.TextChoices):
    """
    What caused a level change. Stored on WriterLevelChangeLog.
    """
    SYSTEM = "system", "Automated System"
    ADMIN = "admin", "Admin"
    WEEKLY_TASK = "weekly_task", "Weekly Evaluation"
    ONBOARDING = "onboarding", "Onboarding"