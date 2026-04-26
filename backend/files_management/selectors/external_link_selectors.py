from __future__ import annotations

from django.db.models import QuerySet

from files_management.enums import ExternalFileReviewStatus
from files_management.models import ExternalFileLink


class ExternalFileLinkSelector:
    """
    Read helpers for external file links.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[ExternalFileLink]:
        return ExternalFileLink.objects.filter(website=website)

    @staticmethod
    def pending_for_website(*, website) -> QuerySet[ExternalFileLink]:
        return ExternalFileLink.objects.filter(
            website=website,
            review_status=ExternalFileReviewStatus.PENDING,
            is_active=True,
        )

    @staticmethod
    def by_id_for_website(
        *,
        link_id: int,
        website,
    ) -> ExternalFileLink | None:
        return ExternalFileLink.objects.filter(
            id=link_id,
            website=website,
        ).first()