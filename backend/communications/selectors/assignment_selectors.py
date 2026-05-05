from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationThreadAssignment


class CommunicationThreadAssignmentSelector:
    """
    Read helpers for thread assignments.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationThreadAssignment]:
        """
        Return all assignments for a website.
        """
        return CommunicationThreadAssignment.objects.filter(website=website)

    @staticmethod
    def active_for_thread(
        *,
        website,
        thread,
    ) -> QuerySet[CommunicationThreadAssignment]:
        """
        Return active assignments for a thread.
        """
        return (
            CommunicationThreadAssignment.objects
            .filter(
                website=website,
                thread=thread,
                is_active=True,
            )
            .select_related("thread", "assigned_to", "assigned_by")
            .order_by("assigned_at", "id")
        )

    @staticmethod
    def active_for_user(
        *,
        website,
        user,
    ) -> QuerySet[CommunicationThreadAssignment]:
        """
        Return active assignments for a user.
        """
        return (
            CommunicationThreadAssignment.objects
            .filter(
                website=website,
                assigned_to=user,
                is_active=True,
            )
            .select_related("thread", "assigned_to", "assigned_by")
            .order_by("-assigned_at", "-id")
        )

    @staticmethod
    def get_active_for_user_thread(
        *,
        website,
        user,
        thread,
    ) -> CommunicationThreadAssignment | None:
        """
        Return active assignment for a user and thread.
        """
        return (
            CommunicationThreadAssignment.objects
            .filter(
                website=website,
                assigned_to=user,
                thread=thread,
                is_active=True,
            )
            .select_related("thread", "assigned_to", "assigned_by")
            .first()
        )

    @staticmethod
    def is_assigned_to_thread(*, website, user, thread) -> bool:
        """
        Check whether a user is actively assigned to a thread.
        """
        return CommunicationThreadAssignment.objects.filter(
            website=website,
            assigned_to=user,
            thread=thread,
            is_active=True,
        ).exists()