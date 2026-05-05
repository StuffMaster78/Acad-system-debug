from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationParticipant


class CommunicationParticipantSelector:
    """
    Read helpers for communication participants.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationParticipant]:
        """
        Return all participant records for a website.
        """
        return CommunicationParticipant.objects.filter(website=website)

    @staticmethod
    def for_thread(*, website, thread) -> QuerySet[CommunicationParticipant]:
        """
        Return participants for a thread.
        """
        return (
            CommunicationParticipant.objects
            .filter(website=website, thread=thread)
            .select_related("user", "added_by", "thread")
            .order_by("joined_at", "id")
        )

    @staticmethod
    def active_for_thread(
        *,
        website,
        thread,
    ) -> QuerySet[CommunicationParticipant]:
        """
        Return active participants for a thread.
        """
        return (
            CommunicationParticipant.objects
            .filter(
                website=website,
                thread=thread,
                removed_at__isnull=True,
                can_view=True,
            )
            .select_related("user", "added_by", "thread")
            .order_by("joined_at", "id")
        )

    @staticmethod
    def for_user(*, website, user) -> QuerySet[CommunicationParticipant]:
        """
        Return thread memberships for a user.
        """
        return (
            CommunicationParticipant.objects
            .filter(
                website=website,
                user=user,
                removed_at__isnull=True,
                can_view=True,
            )
            .select_related("thread", "user")
            .order_by("-joined_at", "-id")
        )

    @staticmethod
    def get_for_user_thread(
        *,
        website,
        user,
        thread,
    ) -> CommunicationParticipant | None:
        """
        Return one participant record for a user and thread.
        """
        return (
            CommunicationParticipant.objects
            .filter(
                website=website,
                user=user,
                thread=thread,
            )
            .select_related("user", "thread")
            .first()
        )

    @staticmethod
    def user_can_view_thread(*, website, user, thread) -> bool:
        """
        Check whether a user can view a thread.
        """
        return CommunicationParticipant.objects.filter(
            website=website,
            user=user,
            thread=thread,
            can_view=True,
            removed_at__isnull=True,
        ).exists()

    @staticmethod
    def user_can_send_to_thread(*, website, user, thread) -> bool:
        """
        Check whether a user can send messages to a thread.
        """
        return CommunicationParticipant.objects.filter(
            website=website,
            user=user,
            thread=thread,
            can_view=True,
            can_send=True,
            removed_at__isnull=True,
        ).exists()