from __future__ import annotations

from writer_compensation.models.writer_reward import (
    WriterReward,
)
from notifications_system.enums import (
    NotificationEvent,
    NotificationPriority,
)
from notifications_system.services.notification_service import (
    NotificationService,
)


class RewardNotificationService:
    """
    Emits notifications for writer reward lifecycle events.

    This service does NOT:
        - render templates
        - send emails
        - manage delivery channels

    It only fires domain notifications into the notification system.
    """

    @staticmethod
    def notify_reward_issued(
        *,
        reward: WriterReward,
    ) -> None:
        """
        Notify writer that a reward was successfully issued.
        """

        account_profile = reward.writer.account_profile

        NotificationService.notify(
            event_key=NotificationEvent.WRITER_REWARD_ISSUED,
            recipient=account_profile.user,
            website=reward.website,
            priority=NotificationPriority.HIGH,
            context={
                "reward_id": str(reward.pk),
                "reward_title": reward.reward_title,
                "reward_description": reward.reward_description,
                "reward_amount": str(reward.reward_amount),
                "badge_name": reward.badge_name,
                "average_rating": (
                    str(reward.average_rating)
                    if reward.average_rating is not None
                    else None
                ),
                "percentile_rank": (
                    str(reward.percentile_rank)
                    if reward.percentile_rank is not None
                    else None
                ),
                "review_count": reward.review_count,
                "period_start": (
                    reward.period_start.isoformat()
                    if reward.period_start
                    else None
                ),
                "period_end": (
                    reward.period_end.isoformat()
                    if reward.period_end
                    else None
                ),
            },
        )

    @staticmethod
    def notify_reward_revoked(
        *,
        reward: WriterReward,
        reason: str = "",
    ) -> None:
        """
        Notify writer that a reward was revoked.
        """

        account_profile = reward.writer.account_profile

        NotificationService.notify(
            event_key=NotificationEvent.WRITER_REWARD_REVOKED,
            recipient=account_profile.user,
            website=reward.website,
            priority=NotificationPriority.HIGH,
            is_critical=True,
            context={
                "reward_id": str(reward.pk),
                "reward_title": reward.reward_title,
                "reason": reason,
            },
        )