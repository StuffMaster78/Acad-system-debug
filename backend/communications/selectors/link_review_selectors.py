from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationLinkReview
from communications.models import CommunicationLinkReviewStatus


class CommunicationLinkReviewSelector:
    """
    Read helpers for communication link reviews.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationLinkReview]:
        """
        Return link reviews for a website.
        """
        return (
            CommunicationLinkReview.objects
            .filter(website=website)
            .select_related(
                "thread",
                "message",
                "submitted_by",
                "reviewed_by",
            )
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def pending_for_website(*, website) -> QuerySet[CommunicationLinkReview]:
        """
        Return pending link reviews for a website.
        """
        return (
            CommunicationLinkReview.objects
            .filter(
                website=website,
                status=CommunicationLinkReviewStatus.PENDING,
            )
            .select_related(
                "thread",
                "message",
                "submitted_by",
                "reviewed_by",
            )
            .order_by("created_at", "id")
        )

    @staticmethod
    def for_message(*, website, message) -> QuerySet[CommunicationLinkReview]:
        """
        Return link reviews for a message.
        """
        return (
            CommunicationLinkReview.objects
            .filter(website=website, message=message)
            .select_related(
                "thread",
                "message",
                "submitted_by",
                "reviewed_by",
            )
            .order_by("created_at", "id")
        )

    @staticmethod
    def for_domain(
        *,
        website,
        domain: str,
    ) -> QuerySet[CommunicationLinkReview]:
        """
        Return link reviews for a domain.
        """
        return (
            CommunicationLinkReview.objects
            .filter(website=website, domain__iexact=domain)
            .select_related(
                "thread",
                "message",
                "submitted_by",
                "reviewed_by",
            )
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def has_pending_for_message(*, website, message) -> bool:
        """
        Check whether a message has pending link review records.
        """
        return CommunicationLinkReview.objects.filter(
            website=website,
            message=message,
            status=CommunicationLinkReviewStatus.PENDING,
        ).exists()