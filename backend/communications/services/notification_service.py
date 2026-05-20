from __future__ import annotations

from communications.services.event_recipient_service import (
    CommunicationEventRecipientService,
)
from notifications_system.services.notification_service import (
    NotificationService,
)


class CommunicationNotificationService:
    """
    Bridge communications to the centralized notifications system.
    """

    MESSAGE_CREATED_EVENT = "communications.message.created"
    MESSAGE_FLAGGED_EVENT = "communications.message.flagged"
    THREAD_ESCALATED_EVENT = "communications.thread.escalated"
    LINK_REVIEW_CREATED_EVENT = "communications.link_review.created"

    @staticmethod
    def notify_message_created(*, message) -> None:
        """
        Notify active thread participants about a new message.
        """
        recipient_ids = (
            CommunicationEventRecipientService.message_created_recipients(
                message=message,
            )
        )

        participants = message.thread.participants.filter(
            user_id__in=recipient_ids,
            can_view=True,
            removed_at__isnull=True,
        ).select_related("user")

        for participant in participants:
            NotificationService.notify(
                event_key=(
                    CommunicationNotificationService.MESSAGE_CREATED_EVENT
                ),
                recipient=participant.user,
                website=message.website,
                context={
                    "thread_id": message.thread_id,
                    "message_id": message.pk,
                    "sender_id": (
                        message.sender.pk
                        if message.sender is not None
                        else None
                    ),
                    "message_preview": message.body[:160],
                    "thread_kind": message.thread.kind,
                },
                triggered_by=message.sender,
            )

    @staticmethod
    def notify_message_flagged(*, message, flag) -> None:
        """
        Notify staff when a message is flagged.
        """
        staff_participants = message.thread.participants.filter(
            role__in=["admin", "superadmin", "support"],
            can_view=True,
            removed_at__isnull=True,
        ).select_related("user")

        for participant in staff_participants:
            NotificationService.notify(
                event_key=(
                    CommunicationNotificationService.MESSAGE_FLAGGED_EVENT
                ),
                recipient=participant.user,
                website=message.website,
                context={
                    "thread_id": message.thread_id,
                    "message_id": message.pk,
                    "flag_id": flag.pk,
                    "severity": flag.severity,
                    "reason": flag.reason,
                },
                triggered_by=flag.created_by,
                is_critical=True,
            )

    @staticmethod
    def notify_thread_escalated(*, escalation) -> None:
        """
        Notify staff when a thread is escalated.
        """
        staff_participants = escalation.thread.participants.filter(
            role__in=["admin", "superadmin", "support"],
            can_view=True,
            removed_at__isnull=True,
        ).select_related("user")

        for participant in staff_participants:
            NotificationService.notify(
                event_key=(
                    CommunicationNotificationService.THREAD_ESCALATED_EVENT
                ),
                recipient=participant.user,
                website=escalation.website,
                context={
                    "thread_id": escalation.thread_id,
                    "escalation_id": escalation.pk,
                    "reason": escalation.reason,
                },
                triggered_by=escalation.escalated_by,
                is_critical=True,
            )

    @staticmethod
    def notify_link_review_created(*, review) -> None:
        """
        Notify admin and superadmin users about a pending link review.
        """
        staff_participants = review.thread.participants.filter(
            role__in=["admin", "superadmin"],
            can_view=True,
            removed_at__isnull=True,
        ).select_related("user")

        for participant in staff_participants:
            NotificationService.notify(
                event_key=(
                    CommunicationNotificationService.LINK_REVIEW_CREATED_EVENT
                ),
                recipient=participant.user,
                website=review.website,
                context={
                    "thread_id": review.thread_id,
                    "message_id": review.message_id,
                    "review_id": review.pk,
                    "domain": review.domain,
                    "url": review.url,
                },
                triggered_by=review.submitted_by,
                is_critical=True,
            )
