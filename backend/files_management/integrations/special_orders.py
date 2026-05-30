from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.enums import FilePurpose, FileVisibility
from files_management.models.file_attachment import FileAttachment
from files_management.services import (
    ExternalFileLinkService,
    FileAttachmentService,
    FileUploadService,
    FileVersionService,
)


class SpecialOrderFileIntegrationService:
    """
    Special-order-facing integration for the central file system.

    The special_orders app owns business rules for special orders.
    This integration only handles file upload, versioning, and attachment.

    File categories and their default visibility:

        SPECIAL_ORDER_REFERENCE    — ORDER_PARTICIPANTS (client + writer + staff)
        SPECIAL_ORDER_SCREENSHOT   — STAFF_ONLY (portal screenshots, sensitive)
        SPECIAL_ORDER_CREDENTIAL   — STAFF_ONLY (portal logins, vault pending)
        SPECIAL_ORDER_MILESTONE    — CLIENT_AND_STAFF until funded; guard-gated
        SPECIAL_ORDER_REPORT       — CLIENT_AND_STAFF

    Credential and screenshot files are marked STAFF_ONLY by default.
    Full vault mode (access reason required, per-view audit, delegated
    access with expiry) will be layered on top when the sensitive-file
    feature lands.
    """

    # ------------------------------------------------------------------
    # Client / writer uploads
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def upload_reference_file(
        cls,
        *,
        special_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload a reference or instruction file for a special order.
        """
        return cls._upload_and_attach(
            special_order=special_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.SPECIAL_ORDER_REFERENCE,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            metadata={
                "special_order_file_type": "reference",
                "description": description,
                "source_domain": "special_orders",
            },
        )

    @classmethod
    @transaction.atomic
    def upload_screenshot(
        cls,
        *,
        special_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        description: str = "",
        task_label: str = "",
    ) -> FileAttachment:
        """
        Upload a portal screenshot (e.g. proof of submission, grade page).

        Screenshots are STAFF_ONLY by default. Staff can later widen
        visibility to CLIENT_AND_STAFF after review.
        """
        return cls._upload_and_attach(
            special_order=special_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.SPECIAL_ORDER_SCREENSHOT,
            visibility=FileVisibility.STAFF_ONLY,
            metadata={
                "special_order_file_type": "screenshot",
                "description": description,
                "task_label": task_label,
                "source_domain": "special_orders",
            },
        )

    @classmethod
    @transaction.atomic
    def upload_credential(
        cls,
        *,
        special_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload portal credentials or access files.

        Credentials are STAFF_ONLY and treated as sensitive. Full vault
        mode (delegated access, per-view audit, access reason) will be
        enforced once the sensitive-file feature lands.
        """
        return cls._upload_and_attach(
            special_order=special_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.SPECIAL_ORDER_CREDENTIAL,
            visibility=FileVisibility.STAFF_ONLY,
            metadata={
                "special_order_file_type": "credential",
                "description": description,
                "source_domain": "special_orders",
                "is_sensitive": True,
            },
        )

    @classmethod
    @transaction.atomic
    def upload_milestone_deliverable(
        cls,
        *,
        special_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        milestone=None,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload a deliverable file for a specific funding milestone.

        The attachment is linked to the SpecialOrder via the generic FK.
        The milestone PK is stored in metadata so the delivery guard and
        ops views can resolve which milestone's payment gates this download.

        The attachment is created with purpose SPECIAL_ORDER_MILESTONE and
        delivery_status=PENDING. Call submit_milestone_deliverable() after
        upload to mark it ready for client delivery.
        """
        milestone_id = getattr(milestone, "pk", None)
        milestone_label = getattr(milestone, "label", "")
        milestone_sequence = getattr(milestone, "sequence", None)

        return cls._upload_and_attach(
            special_order=special_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.SPECIAL_ORDER_MILESTONE,
            visibility=FileVisibility.CLIENT_AND_STAFF,
            metadata={
                "special_order_file_type": "milestone_deliverable",
                "milestone_id": milestone_id,
                "milestone_label": milestone_label,
                "milestone_sequence": milestone_sequence,
                "description": description,
                "source_domain": "special_orders",
            },
        )

    @classmethod
    @transaction.atomic
    def upload_report(
        cls,
        *,
        special_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload a report file (progress reports, completion evidence, etc.).
        """
        return cls._upload_and_attach(
            special_order=special_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.SPECIAL_ORDER_REPORT,
            visibility=FileVisibility.CLIENT_AND_STAFF,
            metadata={
                "special_order_file_type": "report",
                "description": description,
                "source_domain": "special_orders",
            },
        )

    # ------------------------------------------------------------------
    # Delivery submission
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def submit_milestone_deliverable(
        cls,
        *,
        attachment: FileAttachment,
        submitted_by,
        on_behalf_of=None,
        reason: str = "",
    ) -> FileAttachment:
        """
        Mark a milestone deliverable as submitted for delivery.

        Validates that the file's scan has passed before flipping the
        submitted flag. The delivery guard will then check milestone
        payment status before generating a signed download URL.

        Args:
            attachment:    The SPECIAL_ORDER_MILESTONE attachment to submit.
            submitted_by:  Actor pressing Submit.
            on_behalf_of:  Writer represented by staff, if applicable.
            reason:        Required when on_behalf_of is set.
        """
        from files_management.services.file_delivery_guard_service import (
            FileDeliveryGuardService,
        )
        return FileDeliveryGuardService.submit_as_final(
            attachment=attachment,
            submitted_by=submitted_by,
            on_behalf_of=on_behalf_of,
            reason=reason,
        )

    # ------------------------------------------------------------------
    # External links
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def submit_external_link(
        cls,
        *,
        special_order,
        submitted_by,
        url: str,
        purpose: str,
        title: str = "",
    ) -> FileAttachment:
        """
        Submit and attach an external file link to a special order.
        """
        external_link = ExternalFileLinkService.submit_link(
            website=special_order.website,
            submitted_by=submitted_by,
            url=url,
            purpose=purpose,
            title=title,
        )
        return FileAttachmentService.attach_external_link(
            website=special_order.website,
            obj=special_order,
            external_link=external_link,
            purpose=purpose,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            attached_by=submitted_by,
            display_name=title,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _upload_and_attach(
        cls,
        *,
        special_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        purpose: str,
        visibility: str,
        is_primary: bool = False,
        display_name: str = "",
        notes: str = "",
        metadata: dict | None = None,
    ) -> FileAttachment:
        metadata = {
            **(metadata or {}),
            "special_order_file_version": cls._next_attachment_version(
                special_order=special_order,
                purpose=purpose,
            ),
        }

        managed_file = FileUploadService.upload_file(
            website=special_order.website,
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
            website=special_order.website,
            obj=special_order,
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
    def _next_attachment_version(*, special_order, purpose: str) -> int:
        content_type = ContentType.objects.get_for_model(
            special_order,
            for_concrete_model=False,
        )
        latest = (
            FileAttachment.objects.filter(
                website=special_order.website,
                content_type=content_type,
                object_id=special_order.pk,
                purpose=purpose,
            )
            .order_by("-attached_at")
            .first()
        )
        if latest:
            return int(
                (latest.metadata or {}).get("special_order_file_version", 1)
            ) + 1
        return 1
