from __future__ import annotations

from django.db.models import QuerySet

from files_management.enums import DeletionRequestStatus
from files_management.models import FileDeletionRequest


class FileDeletionRequestSelector:
    """
    Read helpers for governed file deletion requests.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[FileDeletionRequest]:
        return FileDeletionRequest.objects.filter(website=website)

    @staticmethod
    def pending_for_website(*, website) -> QuerySet[FileDeletionRequest]:
        return FileDeletionRequest.objects.filter(
            website=website,
            status=DeletionRequestStatus.PENDING,
        )

    @staticmethod
    def by_id_for_website(
        *,
        request_id: int,
        website,
    ) -> FileDeletionRequest | None:
        return FileDeletionRequest.objects.filter(
            id=request_id,
            website=website,
        ).first()