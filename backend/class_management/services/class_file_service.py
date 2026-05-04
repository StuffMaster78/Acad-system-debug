from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from class_management.models import ClassOrder, ClassScopeItem, ClassTask


class ClassFileService:
    """
    Bridge class orders to files_management.

    The files_management app owns uploads, storage, access control,
    signed URLs, deletion requests, scans, and audit logs.

    This service only attaches files to class domain objects.
    """

    @classmethod
    @transaction.atomic
    def attach_to_class_order(
        cls,
        *,
        class_order: ClassOrder,
        uploaded_file,
        uploaded_by,
        category: str,
        visibility: str,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Attach a file to the whole class order.
        """
        return cls._create_file_record(
            owner=class_order,
            website=class_order.website,
            uploaded_file=uploaded_file,
            uploaded_by=uploaded_by,
            category=category,
            visibility=visibility,
            metadata=metadata,
        )

    @classmethod
    @transaction.atomic
    def attach_to_task(
        cls,
        *,
        task: ClassTask,
        uploaded_file,
        uploaded_by,
        category: str,
        visibility: str,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Attach a file to a specific class task.
        """
        return cls._create_file_record(
            owner=task,
            website=task.class_order.website,
            uploaded_file=uploaded_file,
            uploaded_by=uploaded_by,
            category=category,
            visibility=visibility,
            metadata=metadata,
        )

    @classmethod
    @transaction.atomic
    def attach_to_scope_item(
        cls,
        *,
        scope_item: ClassScopeItem,
        uploaded_file,
        uploaded_by,
        category: str,
        visibility: str,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Attach a file to a workload item.
        """
        return cls._create_file_record(
            owner=scope_item,
            website=scope_item.class_order.website,
            uploaded_file=uploaded_file,
            uploaded_by=uploaded_by,
            category=category,
            visibility=visibility,
            metadata=metadata,
        )

    @classmethod
    def list_class_order_files(
        cls,
        *,
        class_order: ClassOrder,
    ):
        """
        Return files attached directly to a class order.
        """
        from files_management.models import ManagedFile

        content_type = ContentType.objects.get_for_model(class_order)

        return ManagedFile.objects.filter(
            website=class_order.website,
            content_type=content_type,
            object_id=class_order.pk,
        ).order_by("-created_at")

    @classmethod
    def list_task_files(
        cls,
        *,
        task: ClassTask,
    ):
        """
        Return files attached to a class task.
        """
        from files_management.models import ManagedFile

        content_type = ContentType.objects.get_for_model(task)

        return ManagedFile.objects.filter(
            website=task.class_order.website,
            content_type=content_type,
            object_id=task.pk,
        ).order_by("-created_at")

    @classmethod
    def _create_file_record(
        cls,
        *,
        owner,
        website,
        uploaded_file,
        uploaded_by,
        category: str,
        visibility: str,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Create a files_management record for a class object.

        Adjust field names to your actual files_management model.
        """
        from files_management.models import ManagedFile

        content_type = ContentType.objects.get_for_model(owner)

        return ManagedFile.objects.create(
            website=website,
            content_type=content_type,
            object_id=owner.pk,
            uploaded_by=uploaded_by,
            file=uploaded_file,
            category=category,
            visibility=visibility,
            metadata=metadata or {},
        )