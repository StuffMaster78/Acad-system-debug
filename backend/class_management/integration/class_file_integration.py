from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from class_management.services.class_file_guard_service import (
    ClassFileGuardService,
)


class ClassFileIntegrationService:
    """
    Bridge class objects to files_management.

    files_management owns storage, signed URLs, deletion requests,
    moderation, scans, and file access.
    """

    @staticmethod
    @transaction.atomic
    def attach_file(
        *,
        owner,
        website,
        uploaded_by,
        uploaded_file,
        category: str,
        visibility: str,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Attach an uploaded file to a class-related object.
        """
        from files_management.models import ManagedFile

        ClassFileGuardService.validate_file_context(
            category=category,
            visibility=visibility,
            uploaded_by=uploaded_by,
        )

        content_type = ContentType.objects.get_for_model(owner)

        return ManagedFile.objects.create(
            website=website,
            content_type=content_type,
            object_id=ClassFileIntegrationService._get_pk(owner),
            uploaded_by=uploaded_by,
            file=uploaded_file,
            category=category,
            visibility=visibility,
            metadata=metadata or {},
        )

    @staticmethod
    def list_files_for_owner(*, owner, website):
        """
        Return files attached to a class-related object.
        """
        from files_management.models import ManagedFile

        content_type = ContentType.objects.get_for_model(owner)

        return ManagedFile.objects.filter(
            website=website,
            content_type=content_type,
            object_id=ClassFileIntegrationService._get_pk(owner),
        ).order_by("-created_at")

    @staticmethod
    def _get_pk(obj: Any) -> Any:
        """
        Return an object's primary key safely.
        """
        return getattr(obj, "pk", None)