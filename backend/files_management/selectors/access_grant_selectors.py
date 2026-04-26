from __future__ import annotations

from django.db.models import Q, QuerySet
from django.utils import timezone

from files_management.models import FileAccessGrant


class FileAccessGrantSelector:
    """
    Read helpers for explicit file access grants.
    """

    @staticmethod
    def active_for_user(
        *,
        user,
        website,
    ) -> QuerySet[FileAccessGrant]:
        """
        Return active grants for a user within a website.
        """

        now = timezone.now()

        return FileAccessGrant.objects.filter(
            website=website,
            grantee=user,
            revoked_at__isnull=True,
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        )

    @staticmethod
    def has_active_grant(
        *,
        user,
        website,
        managed_file,
        action: str,
        attachment=None,
    ) -> bool:
        """
        Return whether a user has an active grant for a file action.
        """

        queryset = FileAccessGrantSelector.active_for_user(
            user=user,
            website=website,
        ).filter(
            managed_file=managed_file,
            action=action,
        )

        if attachment is not None:
            queryset = queryset.filter(
                Q(attachment=attachment) | Q(attachment__isnull=True)
            )

        return queryset.exists()

    @staticmethod
    def for_file(
        *,
        managed_file,
    ) -> QuerySet[FileAccessGrant]:
        """
        Return grants associated with a managed file.
        """

        return FileAccessGrant.objects.filter(
            managed_file=managed_file,
        )