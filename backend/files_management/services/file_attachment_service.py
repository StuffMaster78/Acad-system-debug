from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction

from files_management.models import (
    ExternalFileLink,
    FileAttachment,
    ManagedFile,
)


class FileAttachmentService:
    """
    Handles linking files to domain objects.

    This service is intentionally generic. Orders, messages, profiles,
    CMS, support tickets, classes, and payments can all attach files
    without adding file fields to every model.
    """

    @classmethod
    @transaction.atomic
    def attach_managed_file(
        cls,
        *,
        website,
        obj,
        managed_file: ManagedFile,
        purpose: str,
        visibility: str,
        attached_by=None,
        is_primary: bool = False,
        display_name: str = "",
        notes: str = "",
        metadata: dict | None = None,
    ) -> FileAttachment:
        """
        Attach an uploaded file to a domain object.
        """

        cls._validate_website_match(
            website=website,
            source=managed_file,
        )

        attachment = FileAttachment(
            website=website,
            managed_file=managed_file,
            content_type=ContentType.objects.get_for_model(
                obj,
                for_concrete_model=False,
            ),
            object_id=obj.pk,
            purpose=purpose,
            visibility=visibility,
            is_primary=is_primary,
            attached_by=attached_by,
            display_name=display_name,
            notes=notes,
            metadata=metadata or {},
        )
        attachment.full_clean()
        attachment.save()

        if is_primary:
            cls._clear_other_primary_attachments(
                attachment=attachment,
            )

        return attachment

    @classmethod
    @transaction.atomic
    def attach_external_link(
        cls,
        *,
        website,
        obj,
        external_link: ExternalFileLink,
        purpose: str,
        visibility: str,
        attached_by=None,
        is_primary: bool = False,
        display_name: str = "",
        notes: str = "",
        metadata: dict | None = None,
    ) -> FileAttachment:
        """
        Attach an external file link to a domain object.
        """

        cls._validate_website_match(
            website=website,
            source=external_link,
        )

        attachment = FileAttachment(
            website=website,
            external_link=external_link,
            content_type=ContentType.objects.get_for_model(
                obj,
                for_concrete_model=False,
            ),
            object_id=obj.pk,
            purpose=purpose,
            visibility=visibility,
            is_primary=is_primary,
            attached_by=attached_by,
            display_name=display_name,
            notes=notes,
            metadata=metadata or {},
        )
        attachment.full_clean()
        attachment.save()

        if is_primary:
            cls._clear_other_primary_attachments(
                attachment=attachment,
            )

        return attachment

    @classmethod
    @transaction.atomic
    def deactivate_attachment(
        cls,
        *,
        attachment: FileAttachment,
        deactivated_by=None,
        reason: str = "",
    ) -> FileAttachment:
        """
        Soft detach a file from a domain object.

        This does not delete the underlying uploaded file or external
        link. It only removes the attachment from normal user flows.
        """

        attachment.is_active = False

        metadata = dict(attachment.metadata or {})
        metadata["deactivated_by_id"] = getattr(
            deactivated_by,
            "id",
            None,
        )
        metadata["deactivation_reason"] = reason

        attachment.metadata = metadata
        attachment.full_clean()
        attachment.save(update_fields=["is_active", "metadata", "updated_at"])

        return attachment

    @staticmethod
    def _validate_website_match(
        *,
        website,
        source,
    ) -> None:
        """
        Validate that a source belongs to the expected website.
        """

        if source.website_id != website.id:
            raise ValidationError(
                "File source must belong to the same website."
            )

    @staticmethod
    def _clear_other_primary_attachments(
        *,
        attachment: FileAttachment,
    ) -> None:
        """
        Ensure only one primary attachment per object and purpose.
        """

        FileAttachment.objects.filter(
            website=attachment.website,
            content_type=attachment.content_type,
            object_id=attachment.object_id,
            purpose=attachment.purpose,
            is_primary=True,
        ).exclude(id=attachment.pk).update(is_primary=False)