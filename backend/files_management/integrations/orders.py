from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.enums import FilePurpose, FileVisibility
from files_management.models import FileAttachment
from files_management.services import (
    ExternalFileLinkService,
    FileAttachmentService,
    FileUploadService,
)


class OrderFileIntegrationService:
    """
    Order-facing integration for the central file system.

    The orders app owns order business rules. This integration only
    handles file upload, external link submission, and attachment.
    """

    @classmethod
    @transaction.atomic
    def upload_instruction_file(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Upload and attach an order instruction file.
        """

        return cls._upload_and_attach(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.ORDER_INSTRUCTION,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
        )

    @classmethod
    @transaction.atomic
    def upload_reference_file(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Upload and attach an order reference file.
        """

        return cls._upload_and_attach(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.ORDER_REFERENCE,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
        )

    @classmethod
    @transaction.atomic
    def upload_draft_file(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Upload and attach a writer draft file.
        """

        return cls._upload_and_attach(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.ORDER_DRAFT,
            visibility=FileVisibility.CLIENT_WRITER_STAFF,
        )

    @classmethod
    @transaction.atomic
    def upload_final_file(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Upload and attach the primary final deliverable.
        """

        return cls._upload_and_attach(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.ORDER_FINAL,
            visibility=FileVisibility.CLIENT_WRITER_STAFF,
            is_primary=True,
        )

    @classmethod
    @transaction.atomic
    def upload_revision_file(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Upload and attach a revision file.
        """

        return cls._upload_and_attach(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.ORDER_REVISION,
            visibility=FileVisibility.CLIENT_WRITER_STAFF,
        )

    @classmethod
    @transaction.atomic
    def submit_external_order_link(
        cls,
        *,
        order,
        submitted_by,
        url: str,
        purpose: str,
        title: str = "",
    ) -> FileAttachment:
        """
        Submit and attach an external order file link.

        Staff review is controlled by FilePolicy for the given purpose.
        """

        external_link = ExternalFileLinkService.submit_link(
            website=order.website,
            submitted_by=submitted_by,
            url=url,
            purpose=purpose,
            title=title,
        )

        return FileAttachmentService.attach_external_link(
            website=order.website,
            obj=order,
            external_link=external_link,
            purpose=purpose,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            attached_by=submitted_by,
            display_name=title,
        )

    @classmethod
    def _upload_and_attach(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
        purpose: str,
        visibility: str,
        is_primary: bool = False,
    ) -> FileAttachment:
        """
        Upload a file and attach it to an order.
        """

        managed_file = FileUploadService.upload_file(
            website=order.website,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=purpose,
            is_public=False,
        )

        return FileAttachmentService.attach_managed_file(
            website=order.website,
            obj=order,
            managed_file=managed_file,
            purpose=purpose,
            visibility=visibility,
            attached_by=uploaded_by,
            is_primary=is_primary,
        )