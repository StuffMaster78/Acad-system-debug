from __future__ import annotations

from django.db.models import Q
from django.db.models import QuerySet

from communications.constants import CommunicationMessageStatus
from communications.models.message import CommunicationMessage
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)


class CommunicationMessageSearchSelector:
    """
    Search helpers for communication messages.
    """

    @staticmethod
    def search_visible_messages(
        *,
        website,
        user,
        query: str,
    ) -> QuerySet[CommunicationMessage]:
        """
        Search messages visible to a user.
        """
        cleaned_query = query.strip()

        base_qs = CommunicationMessage.objects.filter(
            website=website,
            body__icontains=cleaned_query,
        )

        if CommunicationThreadGuardService._has_platform_access(user=user):
            return (
                base_qs
                .select_related("website", "thread", "sender", "parent")
                .order_by("-created_at", "-id")
            )

        return (
            base_qs
            .filter(
                thread__participant_records__user=user,
                thread__participant_records__can_view=True,
                thread__participant_records__removed_at__isnull=True,
            )
            .exclude(is_internal=True)
            .exclude(status=CommunicationMessageStatus.HIDDEN)
            .exclude(status=CommunicationMessageStatus.WITHDRAWN)
            .select_related("website", "thread", "sender", "parent")
            .order_by("-created_at", "-id")
            .distinct()
        )