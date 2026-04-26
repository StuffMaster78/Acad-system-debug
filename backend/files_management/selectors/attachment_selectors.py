from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from files_management.models import FileAttachment


class FileAttachmentSelector:
    """
    Read helpers for FileAttachment records.

    Attachments are the bridge between file sources and domain objects.
    These helpers keep generic relation queries consistent and tenant
    scoped.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[FileAttachment]:
        """
        Return all attachments for a website.
        """

        return FileAttachment.objects.filter(website=website)

    @staticmethod
    def active_for_website(*, website) -> QuerySet[FileAttachment]:
        """
        Return active attachments for a website.
        """

        return FileAttachment.objects.filter(
            website=website,
            is_active=True,
        )

    @staticmethod
    def for_object(
        *,
        website,
        obj,
    ) -> QuerySet[FileAttachment]:
        """
        Return active attachments for a domain object.
        """

        content_type = ContentType.objects.get_for_model(
            obj,
            for_concrete_model=False,
        )

        return FileAttachment.objects.filter(
            website=website,
            content_type=content_type,
            object_id=obj.pk,
            is_active=True,
        )

    @staticmethod
    def for_object_and_purpose(
        *,
        website,
        obj,
        purpose: str,
    ) -> QuerySet[FileAttachment]:
        """
        Return active attachments for an object and purpose.
        """

        return FileAttachmentSelector.for_object(
            website=website,
            obj=obj,
        ).filter(purpose=purpose)

    @staticmethod
    def primary_for_object_and_purpose(
        *,
        website,
        obj,
        purpose: str,
    ) -> FileAttachment | None:
        """
        Return the primary attachment for an object and purpose.
        """

        return FileAttachmentSelector.for_object_and_purpose(
            website=website,
            obj=obj,
            purpose=purpose,
        ).filter(is_primary=True).first()

    @staticmethod
    def by_id_for_website(
        *,
        attachment_id: int,
        website,
    ) -> FileAttachment | None:
        """
        Return an attachment by ID within a website boundary.
        """

        return FileAttachment.objects.filter(
            id=attachment_id,
            website=website,
        ).first()

    @staticmethod
    def for_managed_file(
        *,
        managed_file,
    ) -> QuerySet[FileAttachment]:
        """
        Return active attachments for an uploaded file.
        """

        return FileAttachment.objects.filter(
            managed_file=managed_file,
            is_active=True,
        )

    @staticmethod
    def for_external_link(
        *,
        external_link,
    ) -> QuerySet[FileAttachment]:
        """
        Return active attachments for an external link.
        """

        return FileAttachment.objects.filter(
            external_link=external_link,
            is_active=True,
        )