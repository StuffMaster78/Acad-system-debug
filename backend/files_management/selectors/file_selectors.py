from __future__ import annotations

from django.db.models import QuerySet

from files_management.enums import FileLifecycleStatus, FilePurpose
from files_management.models import ManagedFile


class ManagedFileSelector:
    """
    Read helpers for ManagedFile records.

    Selectors centralize query construction and tenancy filtering. They
    should not mutate data, perform authorization side effects, or call
    external services.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[ManagedFile]:
        """
        Return all files owned by a website.
        """

        return ManagedFile.objects.filter(website=website)

    @staticmethod
    def active_for_website(*, website) -> QuerySet[ManagedFile]:
        """
        Return active files owned by a website.
        """

        return ManagedFile.objects.filter(
            website=website,
            lifecycle_status=FileLifecycleStatus.ACTIVE,
        )

    @staticmethod
    def by_id_for_website(
        *,
        file_id: int,
        website,
    ) -> ManagedFile | None:
        """
        Return a file by ID within a website boundary.
        """

        return ManagedFile.objects.filter(
            id=file_id,
            website=website,
        ).first()

    @staticmethod
    def uploaded_by_user(
        *,
        user,
        website,
    ) -> QuerySet[ManagedFile]:
        """
        Return files uploaded by a specific user within a website.
        """

        return ManagedFile.objects.filter(
            website=website,
            uploaded_by=user,
        )

    @staticmethod
    def attached_to_purpose(
        *,
        website,
        purpose: str | FilePurpose,
    ) -> QuerySet[ManagedFile]:
        """
        Return files attached with a given purpose.
        """

        return ManagedFile.objects.filter(
            website=website,
            attachments__purpose=purpose,
            attachments__is_active=True,
        ).distinct()