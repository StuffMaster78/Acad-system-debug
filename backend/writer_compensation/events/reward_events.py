from __future__ import annotations


class RewardEvents:
    """
    Canonical reward domain events.
    """

    REWARD_ISSUED = "reward.issued"

    REWARD_REVOKED = "reward.revoked"

    REWARD_FAILED = "reward.failed"

    REWARD_FRAUD_FLAGGED = (
        "reward.fraud_flagged"
    )

    ACHIEVEMENT_UNLOCKED = (
        "achievement.unlocked"
    )