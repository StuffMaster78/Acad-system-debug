from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from files_management.models.file_attachment import FileAttachment
from files_management.models.managed_file import ManagedFile


class FileUsageService:
    """
    Tracks and queries where managed files are used.

    This service helps prevent unsafe deletion, supports CMS/file audits,
    and gives admins visibility into all domain objects using a file.
    """

    @staticmethod
    def get_file_attachments(
        *,
        managed_file: ManagedFile,
        include_inactive: bool = False,
    ) -> QuerySet[FileAttachment]:
        """
        Return all attachments that reference a managed file.
        """

        queryset = FileAttachment.objects.filter(
            managed_file=managed_file,
        ).select_related(
            "website",
            "content_type",
            "attached_by",
        )

        if not include_inactive:
            queryset = queryset.filter(is_active=True)

        return queryset

    @classmethod
    def get_usage_count(
        cls,
        *,
        managed_file: ManagedFile,
        include_inactive: bool = False,
    ) -> int:
        """
        Return how many attachments currently reference a managed file.
        """

        return cls.get_file_attachments(
            managed_file=managed_file,
            include_inactive=include_inactive,
        ).count()

    @classmethod
    def is_file_in_use(
        cls,
        *,
        managed_file: ManagedFile,
        include_inactive: bool = False,
    ) -> bool:
        """
        Return whether a managed file is referenced by any attachment.
        """

        return cls.get_file_attachments(
            managed_file=managed_file,
            include_inactive=include_inactive,
        ).exists()

    @classmethod
    def ensure_not_in_use(
        cls,
        *,
        managed_file: ManagedFile,
        include_inactive: bool = False,
    ) -> None:
        """
        Raise an error if the file is still attached to any object.
        """

        if cls.is_file_in_use(
            managed_file=managed_file,
            include_inactive=include_inactive,
        ):
            raise ValueError(
                "This file is still attached to one or more objects."
            )

    @staticmethod
    def get_object_attachments(
        *,
        website,
        obj: Any,
        include_inactive: bool = False,
    ) -> QuerySet[FileAttachment]:
        """
        Return attachments linked to a specific domain object.
        """

        content_type = ContentType.objects.get_for_model(
            obj,
            for_concrete_model=False,
        )

        queryset = FileAttachment.objects.filter(
            website=website,
            content_type=content_type,
            object_id=obj.pk,
        ).select_related(
            "managed_file",
            "external_link",
            "attached_by",
        )

        if not include_inactive:
            queryset = queryset.filter(is_active=True)

        return queryset

    @classmethod
    def get_primary_attachment(
        cls,
        *,
        website,
        obj: Any,
    ) -> FileAttachment | None:
        """
        Return the primary attachment for a domain object, if one exists.
        """

        return cls.get_object_attachments(
            website=website,
            obj=obj,
        ).filter(
            is_primary=True,
        ).first()

    @classmethod
    def get_usage_summary(
        cls,
        *,
        managed_file: ManagedFile,
        include_inactive: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Return a lightweight usage summary for admin/audit displays.
        """

        attachments = cls.get_file_attachments(
            managed_file=managed_file,
            include_inactive=include_inactive,
        )

        summary: list[dict[str, Any]] = []

        for attachment in attachments:
            summary.append(
                {
                    "attachment_id": attachment.pk,
                    "website_id": attachment.website.pk,
                    "content_type": attachment.content_type.model,
                    "object_id": attachment.object_id,
                    "purpose": attachment.purpose,
                    "visibility": attachment.visibility,
                    "is_primary": attachment.is_primary,
                    "is_active": attachment.is_active,
                    "attached_at": attachment.attached_at,
                }
            )

        return summary