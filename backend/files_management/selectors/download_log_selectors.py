from __future__ import annotations

from django.db.models import QuerySet

from files_management.models import FileDownloadLog


class FileDownloadLogSelector:
    """
    Read helpers for file download audit logs.
    """

    @staticmethod
    def for_file(*, managed_file) -> QuerySet[FileDownloadLog]:
        """
        Return download logs for a managed file.
        """

        return FileDownloadLog.objects.filter(
            file=managed_file,
        )

    @staticmethod
    def for_user(
        *,
        user,
        website,
    ) -> QuerySet[FileDownloadLog]:
        """
        Return download logs for a user within a website.

        Website scoping is reached through the managed file relationship.
        """

        return FileDownloadLog.objects.filter(
            downloaded_by=user,
            file__website=website,
        )

    @staticmethod
    def for_website(*, website) -> QuerySet[FileDownloadLog]:
        """
        Return all download logs for a website.
        """

        return FileDownloadLog.objects.filter(
            file__website=website,
        )

    @staticmethod
    def recent_for_website(
        *,
        website,
        limit: int = 100,
    ) -> QuerySet[FileDownloadLog]:
        """
        Return recent download logs for a website.
        """

        return FileDownloadLog.objects.filter(
            file__website=website,
        ).order_by("-downloaded_at")[:limit]