from __future__ import annotations

from django.db.models import QuerySet

from files_management.models import FileCategory


class FileCategorySelector:
    """
    Read helpers for tenant file categories.
    """

    @staticmethod
    def active_for_website(*, website) -> QuerySet[FileCategory]:
        return FileCategory.objects.filter(
            website=website,
            is_active=True,
        )

    @staticmethod
    def by_code(
        *,
        website,
        code: str,
    ) -> FileCategory | None:
        return FileCategory.objects.filter(
            website=website,
            code=code,
            is_active=True,
        ).first()