from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationMessageEdit


class CommunicationMessageEditSelector:
    """
    Read helpers for message edit history.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationMessageEdit]:
        """
        Return all message edits for a website.
        """
        return CommunicationMessageEdit.objects.filter(website=website)

    @staticmethod
    def for_message(*, website, message) -> QuerySet[CommunicationMessageEdit]:
        """
        Return edit history for one message.
        """
        return (
            CommunicationMessageEdit.objects
            .filter(website=website, message=message)
            .select_related("thread", "message", "edited_by")
            .order_by("edited_at", "id")
        )

    @staticmethod
    def for_thread(*, website, thread) -> QuerySet[CommunicationMessageEdit]:
        """
        Return edit history for a thread.
        """
        return (
            CommunicationMessageEdit.objects
            .filter(website=website, thread=thread)
            .select_related("thread", "message", "edited_by")
            .order_by("-edited_at", "-id")
        )

    @staticmethod
    def by_user(*, website, user) -> QuerySet[CommunicationMessageEdit]:
        """
        Return message edits made by a user.
        """
        return (
            CommunicationMessageEdit.objects
            .filter(website=website, edited_by=user)
            .select_related("thread", "message", "edited_by")
            .order_by("-edited_at", "-id")
        )