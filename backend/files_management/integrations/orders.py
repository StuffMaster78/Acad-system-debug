from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.enums import FilePurpose, FileVisibility
from files_management.models import FileAttachment
from files_management.services import (
    ExternalFileLinkService,
    FileAttachmentService,
    FileUploadService,
    FileVersionService,
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
            metadata={
                "order_file_status": "instruction",
                "source_domain": "orders",
            },
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
            metadata={
                "order_file_status": "reference",
                "source_domain": "orders",
            },
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
            metadata={
                "order_file_status": "draft",
                "source_domain": "orders",
            },
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
            metadata={
                "order_file_status": "final",
                "is_final_paper": True,
                "source_domain": "orders",
            },
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
            metadata={
                "order_file_status": "revision",
                "source_domain": "orders",
            },
        )

    @classmethod
    @transaction.atomic
    def upload_style_reference_file(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
        reference_type: str = "previous_paper",
        description: str = "",
        is_visible_to_writer: bool = True,
    ) -> FileAttachment:
        """
        Upload and attach a style reference file.

        This replaces the old order_files.StyleReferenceFile model while
        preserving the useful concepts: reference type, description, and
        writer visibility.
        """

        return cls._upload_and_attach(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.STYLE_REFERENCE,
            visibility=(
                FileVisibility.CLIENT_WRITER_STAFF
                if is_visible_to_writer
                else FileVisibility.CLIENT_AND_STAFF
            ),
            metadata={
                "order_file_status": "style_reference",
                "reference_type": reference_type,
                "description": description,
                "is_visible_to_writer": is_visible_to_writer,
                "source_domain": "orders",
            },
        )

    @classmethod
    @transaction.atomic
    def upload_extra_service_file(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
        service_code: str = "",
        category_code: str = "",
        description: str = "",
        is_downloadable: bool = False,
    ) -> FileAttachment:
        """
        Upload and attach an extra service file such as plagiarism reports.

        Old order_files kept these separately and locked downloads by
        default. Here the same idea is expressed through purpose,
        visibility, active state, and metadata.
        """

        attachment = cls._upload_and_attach(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.EXTRA_SERVICE_FILE,
            visibility=FileVisibility.CLIENT_AND_STAFF,
            metadata={
                "order_file_status": "extra_service",
                "service_code": service_code,
                "category_code": category_code,
                "description": description,
                "is_downloadable": is_downloadable,
                "source_domain": "orders",
            },
        )

        return attachment

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
        display_name: str = "",
        notes: str = "",
        metadata: dict | None = None,
    ) -> FileAttachment:
        """
        Upload a file and attach it to an order.
        """

        metadata = {
            **(metadata or {}),
            "order_file_version": cls._next_attachment_version(
                order=order,
                purpose=purpose,
            ),
        }

        managed_file = FileUploadService.upload_file(
            website=order.website,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=purpose,
            is_public=False,
            metadata=metadata,
        )
        FileVersionService.create_initial_version(
            managed_file=managed_file,
            created_by=uploaded_by,
            notes=notes,
        )

        return FileAttachmentService.attach_managed_file(
            website=order.website,
            obj=order,
            managed_file=managed_file,
            purpose=purpose,
            visibility=visibility,
            attached_by=uploaded_by,
            is_primary=is_primary,
            display_name=display_name,
            notes=notes,
            metadata=metadata,
        )

    @staticmethod
    def _next_attachment_version(*, order, purpose: str) -> int:
        content_type = ContentType.objects.get_for_model(
            order,
            for_concrete_model=False,
        )
        latest = (
            FileAttachment.objects.filter(
                website=order.website,
                content_type=content_type,
                object_id=order.pk,
                purpose=purpose,
            )
            .order_by("-attached_at")
            .first()
        )
        if latest:
            return int((latest.metadata or {}).get("order_file_version", 1)) + 1
        return 1
