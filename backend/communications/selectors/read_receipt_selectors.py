from __future__ import annotations

from django.db.models import Count
from django.db.models import Q
from django.db.models import QuerySet

from communications.constants import CommunicationMessageStatus
from communications.models.message import CommunicationMessage
from communications.models.receipt import CommunicationReadReceipt
from communications.models.thread import CommunicationThread


class CommunicationReadReceiptSelector:
    """
    Read helpers for receipts and unread counts.
    """

    @staticmethod
    def for_message(*, website, message) -> QuerySet[CommunicationReadReceipt]:
        """
        Return receipts for one message.
        """
        return (
            CommunicationReadReceipt.objects
            .filter(website=website, message=message)
            .select_related("message", "thread", "user")
            .order_by("read_at", "id")
        )

    @staticmethod
    def for_thread_user(
        *,
        website,
        thread,
        user,
    ) -> QuerySet[CommunicationReadReceipt]:
        """
        Return receipts for one user in one thread.
        """
        return (
            CommunicationReadReceipt.objects
            .filter(website=website, thread=thread, user=user)
            .select_related("message", "thread", "user")
            .order_by("read_at", "id")
        )

    @staticmethod
    def unread_messages_for_user(
        *,
        website,
        user,
    ) -> QuerySet[CommunicationMessage]:
        """
        Return unread messages for a user.
        """
        return (
            CommunicationMessage.objects
            .filter(
                website=website,
                thread__participants__user=user,
                thread__participants__can_view=True,
                thread__participants__removed_at__isnull=True,
            )
            .exclude(sender=user)
            .exclude(status=CommunicationMessageStatus.HIDDEN)
            .exclude(status=CommunicationMessageStatus.WITHDRAWN)
            .exclude(read_receipts__user=user)
            .distinct()
        )

    @staticmethod
    def unread_count_for_user(*, website, user) -> int:
        """
        Return unread message count for a user.
        """
        return CommunicationReadReceiptSelector.unread_messages_for_user(
            website=website,
            user=user,
        ).count()

    @staticmethod
    def threads_with_unread_counts(
        *,
        website,
        user,
    ) -> QuerySet[CommunicationThread]:
        """
        Return user visible threads annotated with unread_count.
        """
        return (
            CommunicationThread.objects
            .filter(
                website=website,
                participants__user=user,
                participants__can_view=True,
                participants__removed_at__isnull=True,
            )
            .annotate(
                unread_count=Count(
                    "messages",
                    filter=(
                        Q(messages__read_receipts__user__isnull=True)
                        & ~Q(messages__sender=user)
                        & ~Q(messages__status=CommunicationMessageStatus.HIDDEN)
                        & ~Q(
                            messages__status=(
                                CommunicationMessageStatus.WITHDRAWN
                            ),
                        )
                    ),
                    distinct=True,
                ),
            )
            .order_by("-last_message_at", "-created_at", "-id")
        )
