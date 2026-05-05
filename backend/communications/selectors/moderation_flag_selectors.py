from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationModerationFlag
from communications.models import CommunicationModerationStatus


class CommunicationModerationFlagSelector:
    """
    Read helpers for communication moderation flags.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationModerationFlag]:
        """
        Return all moderation flags for a website.
        """
        return CommunicationModerationFlag.objects.filter(website=website)

    @staticmethod
    def open_for_website(
        *,
        website,
    ) -> QuerySet[CommunicationModerationFlag]:
        """
        Return open moderation flags for a website.
        """
        return (
            CommunicationModerationFlag.objects
            .filter(
                website=website,
                status=CommunicationModerationStatus.OPEN,
            )
            .select_related(
                "thread",
                "message",
                "created_by",
                "resolved_by",
            )
            .order_by("created_at", "id")
        )

    @staticmethod
    def for_thread(
        *,
        website,
        thread,
    ) -> QuerySet[CommunicationModerationFlag]:
        """
        Return moderation flags for a thread.
        """
        return (
            CommunicationModerationFlag.objects
            .filter(website=website, thread=thread)
            .select_related(
                "thread",
                "message",
                "created_by",
                "resolved_by",
            )
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def for_message(
        *,
        website,
        message,
    ) -> QuerySet[CommunicationModerationFlag]:
        """
        Return moderation flags for a message.
        """
        return (
            CommunicationModerationFlag.objects
            .filter(website=website, message=message)
            .select_related(
                "thread",
                "message",
                "created_by",
                "resolved_by",
            )
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def has_open_flag(*, website, message) -> bool:
        """
        Check whether a message has an open moderation flag.
        """
        return CommunicationModerationFlag.objects.filter(
            website=website,
            message=message,
            status=CommunicationModerationStatus.OPEN,
        ).exists()