from django.db import models


class EventTypes(models.TextChoices):
    """
    Canonical event types across system.
    """

    REVIEW_CREATED = "review.created", "Review Created"
    REVIEW_APPROVED = "review.approved", "Review Approved"
    REVIEW_REJECTED = "review.rejected", "Review Rejected"
    REVIEW_SHADOWED = "review.shadowed", "Review Shadowed"
    REVIEW_FLAGGED = "review.flagged", "Review Flagged"

    REPUTATION_UPDATED = (
        "reputation.updated",
        "Reputation Updated",
    )


    USER_SUSPENDED = "user.suspended"
    USER_UNSUSPENDED = "user.unsuspended"

    USER_BLACKLISTED = "user.blacklisted"
    USER_UNBLACKLISTED = "user.unblacklisted"

    USER_PROBATION_STARTED = "user.probation.started"
    USER_PROBATION_ENDED = "user.probation.ended"

    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"

    POLICY_EVALUATED = "policy.evaluated"

    COMMAND_EXECUTED = "command.executed"
    COMMAND_FAILED = "command.failed"