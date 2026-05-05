from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from communications.models import CommunicationThreadSLA


class CommunicationThreadSLASelector:
    """
    Read helpers for thread SLA records.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationThreadSLA]:
        """
        Return all SLA records for a website.
        """
        return CommunicationThreadSLA.objects.filter(website=website)

    @staticmethod
    def get_for_thread(*, website, thread) -> CommunicationThreadSLA | None:
        """
        Return SLA record for a thread.
        """
        return (
            CommunicationThreadSLA.objects
            .filter(website=website, thread=thread)
            .select_related("thread")
            .first()
        )

    @staticmethod
    def breached(*, website) -> QuerySet[CommunicationThreadSLA]:
        """
        Return breached SLA records.
        """
        return (
            CommunicationThreadSLA.objects
            .filter(website=website, is_breached=True)
            .select_related("thread")
            .order_by("breached_at", "id")
        )

    @staticmethod
    def due_for_response(*, website) -> QuerySet[CommunicationThreadSLA]:
        """
        Return SLA records that are due for response.
        """
        now = timezone.now()

        return (
            CommunicationThreadSLA.objects
            .filter(
                website=website,
                is_breached=False,
                next_response_due_at__isnull=False,
                next_response_due_at__lte=now,
            )
            .select_related("thread")
            .order_by("next_response_due_at", "id")
        )

    @staticmethod
    def first_response_due(*, website) -> QuerySet[CommunicationThreadSLA]:
        """
        Return SLA records with first response due.
        """
        now = timezone.now()

        return (
            CommunicationThreadSLA.objects
            .filter(
                website=website,
                is_breached=False,
                first_response_due_at__isnull=False,
                first_response_due_at__lte=now,
            )
            .select_related("thread")
            .order_by("first_response_due_at", "id")
        )