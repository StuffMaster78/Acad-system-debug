from dataclasses import dataclass


@dataclass(frozen=True)
class EventTypes:
    """
    Central registry of ALL system events.
    Prevents string drift across services.
    """

    # reviews
    REVIEW_CREATED = "review.created"
    REVIEW_APPROVED = "review.approved"
    REVIEW_REJECTED = "review.rejected"
    REVIEW_SHADOWED = "review.shadowed"

    # reputation
    REPUTATION_RECALCULATED = "reputation.recalculated"

    # bonus
    BONUS_PERFORMANCE = "bonus.performance_awarded"
    BONUS_MILESTONE = "bonus.milestone_awarded"
    BONUS_RETENTION = "bonus.retention_awarded"
    BONUS_REFERRAL = "bonus.referral_awarded"