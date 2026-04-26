from __future__ import annotations

from django.db.models import QuerySet

from files_management.models import FilePolicy


class FilePolicySelector:
    """
    Read helpers for tenant file policies.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[FilePolicy]:
        """
        Return all file policies for a website.
        """

        return FilePolicy.objects.filter(website=website)

    @staticmethod
    def active_for_website(*, website) -> QuerySet[FilePolicy]:
        """
        Return active file policies for a website.
        """

        return FilePolicy.objects.filter(
            website=website,
            is_active=True,
        )

    @staticmethod
    def by_purpose(
        *,
        website,
        purpose: str,
    ) -> FilePolicy | None:
        """
        Return the active policy for a website and purpose.
        """

        return FilePolicy.objects.filter(
            website=website,
            purpose=purpose,
            is_active=True,
        ).first()