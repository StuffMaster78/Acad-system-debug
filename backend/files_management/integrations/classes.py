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


class ClassFileIntegrationService:
    """
    Class-order-facing integration for the central file system.

    The class_management app owns business rules for class orders.
    This integration only handles file upload, versioning, and attachment.

    File categories and their default visibility:

        CLASS_SYLLABUS         — ORDER_PARTICIPANTS (client + writer + staff)
        CLASS_RUBRIC           — ORDER_PARTICIPANTS
        CLASS_ASSIGNMENT       — ORDER_PARTICIPANTS; optionally task-linked
        CLASS_SUBMISSION       — WRITER_AND_STAFF by default; staff may
                                  widen to CLIENT_AND_STAFF after review
        CLASS_SCREENSHOT       — STAFF_ONLY until approved; proof of work
        CLASS_GRADE_EVIDENCE   — CLIENT_AND_STAFF
        CLASS_CREDENTIAL       — STAFF_ONLY; treated as sensitive (vault
                                  mode pending)
        CLASS_FEEDBACK         — CLIENT_AND_STAFF

    When a ClassTask is provided, its PK is stored in attachment metadata
    so task-level file grouping works in the UI without a separate FK.
    """

    # ------------------------------------------------------------------
    # Client uploads
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def upload_syllabus(
        cls,
        *,
        class_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        description: str = "",
    ) -> FileAttachment:
        """Upload a course syllabus file."""
        return cls._upload_and_attach(
            class_order=class_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CLASS_SYLLABUS,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            metadata={
                "class_file_type": "syllabus",
                "description": description,
                "source_domain": "class_management",
            },
        )

    @classmethod
    @transaction.atomic
    def upload_rubric(
        cls,
        *,
        class_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        description: str = "",
    ) -> FileAttachment:
        """Upload a grading rubric file."""
        return cls._upload_and_attach(
            class_order=class_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CLASS_RUBRIC,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            metadata={
                "class_file_type": "rubric",
                "description": description,
                "source_domain": "class_management",
            },
        )

    @classmethod
    @transaction.atomic
    def upload_assignment(
        cls,
        *,
        class_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        task=None,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload an assignment prompt or instructions file.

        Pass a ClassTask instance to link this file to a specific task.
        """
        return cls._upload_and_attach(
            class_order=class_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CLASS_ASSIGNMENT,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            metadata=cls._task_metadata(
                task=task,
                file_type="assignment",
                description=description,
            ),
        )

    # ------------------------------------------------------------------
    # Writer / staff uploads
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def upload_submission(
        cls,
        *,
        class_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        task=None,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload a task submission or draft file.

        Submissions are WRITER_AND_STAFF by default. Staff can widen
        visibility to CLIENT_AND_STAFF once the submission is reviewed
        and approved.

        Pass a ClassTask instance to link this file to a specific task.
        """
        return cls._upload_and_attach(
            class_order=class_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CLASS_SUBMISSION,
            visibility=FileVisibility.WRITER_AND_STAFF,
            metadata=cls._task_metadata(
                task=task,
                file_type="submission",
                description=description,
            ),
        )

    @classmethod
    @transaction.atomic
    def upload_screenshot(
        cls,
        *,
        class_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        task=None,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload a portal screenshot (submission proof, grade page, etc.).

        Screenshots default to STAFF_ONLY. Staff approve and widen
        visibility before the client can view proof.

        Pass a ClassTask instance to link this screenshot to a specific task.
        """
        return cls._upload_and_attach(
            class_order=class_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CLASS_SCREENSHOT,
            visibility=FileVisibility.STAFF_ONLY,
            metadata=cls._task_metadata(
                task=task,
                file_type="screenshot",
                description=description,
            ),
        )

    @classmethod
    @transaction.atomic
    def upload_grade_evidence(
        cls,
        *,
        class_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload a grade screenshot or feedback document.

        Grade evidence is visible to client and staff immediately.
        """
        return cls._upload_and_attach(
            class_order=class_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CLASS_GRADE_EVIDENCE,
            visibility=FileVisibility.CLIENT_AND_STAFF,
            metadata={
                "class_file_type": "grade_evidence",
                "description": description,
                "source_domain": "class_management",
            },
        )

    @classmethod
    @transaction.atomic
    def upload_credential(
        cls,
        *,
        class_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload portal credentials or access files.

        Credentials are STAFF_ONLY and flagged as sensitive in metadata.
        Full vault mode (delegated access, per-view audit, access reason)
        will be enforced once the sensitive-file feature lands.
        """
        return cls._upload_and_attach(
            class_order=class_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CLASS_CREDENTIAL,
            visibility=FileVisibility.STAFF_ONLY,
            metadata={
                "class_file_type": "credential",
                "description": description,
                "source_domain": "class_management",
                "is_sensitive": True,
            },
        )

    @classmethod
    @transaction.atomic
    def upload_feedback(
        cls,
        *,
        class_order,
        uploaded_by,
        uploaded_file: UploadedFile,
        description: str = "",
    ) -> FileAttachment:
        """
        Upload instructor feedback or graded work returned to the student.
        """
        return cls._upload_and_attach(
            class_order=class_order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.CLASS_FEEDBACK,
            visibility=FileVisibility.CLIENT_AND_STAFF,
            metadata={
                "class_file_type": "feedback",
                "description": description,
                "source_domain": "class_management",
            },
        )

    # ------------------------------------------------------------------
    # External links
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def submit_external_link(
        cls,
        *,
        class_order,
        submitted_by,
        url: str,
        purpose: str,
        title: str = "",
        task=None,
    ) -> FileAttachment:
        """
        Submit and attach an external file link to a class order.

        Pass a ClassTask to associate the link with a specific task.
        """
        external_link = ExternalFileLinkService.submit_link(
            website=class_order.website,
            submitted_by=submitted_by,
            url=url,
            purpose=purpose,
            title=title,
            metadata=cls._task_metadata(task=task, file_type="external_link"),
        )
        return FileAttachmentService.attach_external_link(
            website=class_order.website,
            obj=class_order,
            external_link=external_link,
            purpose=purpose,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            attached_by=submitted_by,
            display_name=title,
            metadata=cls._task_metadata(task=task, file_type="external_link"),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _upload_and_attach(
        cls,
        *,
        class_order,
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
            "class_file_version": cls._next_attachment_version(
                class_order=class_order,
                purpose=purpose,
            ),
        }

        managed_file = FileUploadService.upload_file(
            website=class_order.website,
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
            website=class_order.website,
            obj=class_order,
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
    def _next_attachment_version(*, class_order, purpose: str) -> int:
        content_type = ContentType.objects.get_for_model(
            class_order,
            for_concrete_model=False,
        )
        latest = (
            FileAttachment.objects.filter(
                website=class_order.website,
                content_type=content_type,
                object_id=class_order.pk,
                purpose=purpose,
            )
            .order_by("-attached_at")
            .first()
        )
        if latest:
            return int(
                (latest.metadata or {}).get("class_file_version", 1)
            ) + 1
        return 1

    @staticmethod
    def _task_metadata(
        *,
        task=None,
        file_type: str = "",
        description: str = "",
    ) -> dict:
        """Build metadata dict with optional task linkage."""
        return {
            "class_file_type": file_type,
            "description": description,
            "task_id": getattr(task, "pk", None),
            "task_title": getattr(task, "title", ""),
            "source_domain": "class_management",
        }
