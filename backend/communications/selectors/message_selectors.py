from __future__ import annotations

from django.db.models import QuerySet

from communications.constants import CommunicationMessageStatus
from communications.models.message import CommunicationMessage
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)


class CommunicationMessageSelector:
    """
    Read helpers for communication messages.
    """

    @staticmethod
    def visible_to_user(*, website, user) -> QuerySet[CommunicationMessage]:
        """
        Return messages visible to a user.
        """
        base_qs = CommunicationMessage.objects.all()

        if CommunicationThreadGuardService._has_platform_access(user=user):
            return base_qs

        return (
            base_qs
            .filter(
                thread__participants__user=user,
                thread__participants__can_view=True,
                thread__participants__removed_at__isnull=True,
            )
            .exclude(is_internal=True)
            .exclude(status=CommunicationMessageStatus.HIDDEN)
            .exclude(status=CommunicationMessageStatus.WITHDRAWN)
            .distinct()
        )

    @staticmethod
    def visible_for_thread(
        *,
        website,
        user,
        thread,
    ) -> QuerySet[CommunicationMessage]:
        """
        Return messages visible to a user in one thread.
        """
        base_qs = CommunicationMessage.objects.filter(
            website=website,
            thread=thread,
        )

        if CommunicationThreadGuardService._has_platform_access(user=user):
            return base_qs.order_by("created_at", "id")

        return (
            base_qs
            .filter(
                thread__participants__user=user,
                thread__participants__can_view=True,
                thread__participants__removed_at__isnull=True,
            )
            .exclude(is_internal=True)
            .exclude(status=CommunicationMessageStatus.HIDDEN)
            .exclude(status=CommunicationMessageStatus.WITHDRAWN)
            .order_by("created_at", "id")
            .distinct()
        )

    @staticmethod
    def for_thread(
        *,
        website,
        thread,
    ) -> QuerySet[CommunicationMessage]:
        """
        Return all messages for a thread.
        """
        return (
            CommunicationMessage.objects
            .filter(website=website, thread=thread)
            .select_related("sender", "thread", "parent")
            .order_by("created_at", "id")
        )
