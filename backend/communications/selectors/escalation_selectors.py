from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationEscalation
from communications.models import CommunicationEscalationStatus


class CommunicationEscalationSelector:
    """
    Read helpers for communication escalations.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationEscalation]:
        """
        Return all escalations for a website.
        """
        return CommunicationEscalation.objects.filter(website=website)

    @staticmethod
    def open_for_website(*, website) -> QuerySet[CommunicationEscalation]:
        """
        Return open escalations for a website.
        """
        return (
            CommunicationEscalation.objects
            .filter(
                website=website,
                status=CommunicationEscalationStatus.OPEN,
            )
            .select_related("thread", "escalated_by", "resolved_by")
            .order_by("escalated_at", "id")
        )

    @staticmethod
    def for_thread(*, website, thread) -> QuerySet[CommunicationEscalation]:
        """
        Return escalations for a thread.
        """
        return (
            CommunicationEscalation.objects
            .filter(website=website, thread=thread)
            .select_related("thread", "escalated_by", "resolved_by")
            .order_by("-escalated_at", "-id")
        )

    @staticmethod
    def created_by_user(
        *,
        website,
        user,
    ) -> QuerySet[CommunicationEscalation]:
        """
        Return escalations created by a user.
        """
        return (
            CommunicationEscalation.objects
            .filter(website=website, escalated_by=user)
            .select_related("thread", "escalated_by", "resolved_by")
            .order_by("-escalated_at", "-id")
        )

    @staticmethod
    def has_open_escalation(*, website, thread) -> bool:
        """
        Check whether a thread has an open escalation.
        """
        return CommunicationEscalation.objects.filter(
            website=website,
            thread=thread,
            status=CommunicationEscalationStatus.OPEN,
        ).exists()