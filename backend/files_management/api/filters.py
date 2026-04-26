from __future__ import annotations

from django.db.models import Q, QuerySet


class FileQueryFilter:
    """
    Small query helper for file listing endpoints.
    """

    @staticmethod
    def apply_search(
        *,
        queryset: QuerySet,
        query: str,
    ) -> QuerySet:
        """
        Filter files by filename, MIME type, or storage key.
        """

        if not query:
            return queryset

        return queryset.filter(
            Q(original_name__icontains=query)
            | Q(mime_type__icontains=query)
            | Q(storage_key__icontains=query)
        )

    @staticmethod
    def apply_status(
        *,
        queryset: QuerySet,
        status: str,
    ) -> QuerySet:
        """
        Filter files by lifecycle status.
        """

        if not status:
            return queryset

        return queryset.filter(lifecycle_status=status)

    @staticmethod
    def apply_kind(
        *,
        queryset: QuerySet,
        kind: str,
    ) -> QuerySet:
        """
        Filter files by broad file kind.
        """

        if not kind:
            return queryset

        return queryset.filter(file_kind=kind)