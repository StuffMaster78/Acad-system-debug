from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.enums import FilePurpose, FileVisibility
from files_management.models import FileAttachment
from files_management.services import (
    FileAttachmentService,
    FileUploadService,
)


class CmsFileIntegrationService:
    """
    CMS-facing integration for content assets.

    CMS apps own publishing, SEO metadata, and content workflow rules.
    This integration stores files and attaches them to content objects.
    """

    @classmethod
    @transaction.atomic
    def upload_featured_image(
        cls,
        *,
        content_object,
        uploaded_by,
        uploaded_file: UploadedFile,
        alt_text: str = "",
        caption: str = "",
    ) -> FileAttachment:
        return cls._upload_and_attach(
            content_object=content_object,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CMS_FEATURED_IMAGE,
            visibility=FileVisibility.CMS_PUBLIC,
            is_primary=True,
            metadata={
                "alt_text": alt_text,
                "caption": caption,
            },
        )

    @classmethod
    @transaction.atomic
    def upload_inline_image(
        cls,
        *,
        content_object,
        uploaded_by,
        uploaded_file: UploadedFile,
        alt_text: str = "",
        caption: str = "",
    ) -> FileAttachment:
        return cls._upload_and_attach(
            content_object=content_object,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CMS_INLINE_IMAGE,
            visibility=FileVisibility.CMS_PUBLIC,
            metadata={
                "alt_text": alt_text,
                "caption": caption,
            },
        )

    @classmethod
    @transaction.atomic
    def upload_downloadable_resource(
        cls,
        *,
        content_object,
        uploaded_by,
        uploaded_file: UploadedFile,
        title: str = "",
    ) -> FileAttachment:
        return cls._upload_and_attach(
            content_object=content_object,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CMS_DOWNLOAD,
            visibility=FileVisibility.CMS_PUBLIC,
            display_name=title,
        )

    @classmethod
    def _upload_and_attach(
        cls,
        *,
        content_object,
        uploaded_by,
        uploaded_file: UploadedFile,
        purpose: str,
        visibility: str,
        is_primary: bool = False,
        display_name: str = "",
        metadata: dict | None = None,
    ) -> FileAttachment:
        managed_file = FileUploadService.upload_file(
            website=content_object.website,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=purpose,
            is_public=True,
            metadata=metadata or {},
        )

        return FileAttachmentService.attach_managed_file(
            website=content_object.website,
            obj=content_object,
            managed_file=managed_file,
            purpose=purpose,
            visibility=visibility,
            attached_by=uploaded_by,
            is_primary=is_primary,
            display_name=display_name,
            metadata=metadata or {},
        )