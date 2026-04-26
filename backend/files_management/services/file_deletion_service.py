from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from files_management.enums import (
    DeletionRequestScope,
    DeletionRequestStatus,
    FileAccessAction,
    FileLifecycleStatus,
)
from files_management.exceptions import FileDeletionError
from files_management.models import FileAttachment, FileDeletionRequest
from files_management.services.file_access_service import FileAccessService
from files_management.services.file_attachment_service import (
    FileAttachmentService,
)
from files_management.storage import FileStorageBackend


class FileDeletionService:
    """
    Handles governed file deletion workflows.

    Clients and writers must not directly delete files. They create
    deletion requests. Staff then reviews the request and decides
    whether to detach the file from one context, archive the uploaded
    file, or physically delete it when retention rules allow.

    This preserves evidence, protects disputes, and keeps audit trails
    intact.
    """

    @classmethod
    @transaction.atomic
    def request_deletion(
        cls,
        *,
        website,
        requested_by,
        attachment: FileAttachment,
        reason: str,
        scope: str = DeletionRequestScope.DETACH_ONLY,
    ) -> FileDeletionRequest:
        """
        Create a deletion request for an attachment.

        Normal users should use this method instead of direct deletion.
        """

        if not reason.strip():
            raise FileDeletionError("A deletion reason is required.")

        if attachment.website.pk != website.pk:
            raise FileDeletionError("Attachment does not belong to website.")

        if not cls.can_request_deletion(
            user=requested_by,
            website=website,
            attachment=attachment,
        ):
            raise FileDeletionError(
                "You cannot request deletion for this file."
            )

        managed_file = attachment.managed_file
        external_link = attachment.external_link

        if managed_file is None and external_link is None:
            raise FileDeletionError(
                "Attachment has no deletable source."
            )

        return FileDeletionRequest.objects.create(
            website=website,
            managed_file=managed_file,
            attachment=attachment,
            external_link=external_link,
            requested_by=requested_by,
            reason=reason.strip(),
            scope=scope,
            status=DeletionRequestStatus.PENDING,
        )

    @classmethod
    def can_request_deletion(
        cls,
        *,
        user,
        website,
        attachment: FileAttachment,
    ) -> bool:
        """
        Return whether a user can request deletion for an attachment.
        """

        return FileAccessService.can_access(
            user=user,
            website=website,
            attachment=attachment,
            action=FileAccessAction.VIEW,
        )

    @classmethod
    @transaction.atomic
    def approve_request(
        cls,
        *,
        deletion_request: FileDeletionRequest,
        reviewed_by,
        admin_comment: str = "",
    ) -> FileDeletionRequest:
        """
        Approve a deletion request without completing removal yet.
        """

        cls._ensure_pending(deletion_request=deletion_request)

        deletion_request.status = DeletionRequestStatus.APPROVED
        deletion_request.reviewed_by = reviewed_by
        deletion_request.reviewed_at = timezone.now()
        deletion_request.admin_comment = admin_comment
        deletion_request.full_clean()
        deletion_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "admin_comment",
                "updated_at",
            ]
        )

        return deletion_request

    @classmethod
    @transaction.atomic
    def reject_request(
        cls,
        *,
        deletion_request: FileDeletionRequest,
        reviewed_by,
        admin_comment: str,
    ) -> FileDeletionRequest:
        """
        Reject a deletion request after staff review.
        """

        cls._ensure_pending(deletion_request=deletion_request)

        if not admin_comment.strip():
            raise FileDeletionError("Rejection comment is required.")

        deletion_request.status = DeletionRequestStatus.REJECTED
        deletion_request.reviewed_by = reviewed_by
        deletion_request.reviewed_at = timezone.now()
        deletion_request.admin_comment = admin_comment.strip()
        deletion_request.full_clean()
        deletion_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "admin_comment",
                "updated_at",
            ]
        )

        return deletion_request

    @classmethod
    @transaction.atomic
    def complete_request(
        cls,
        *,
        deletion_request: FileDeletionRequest,
        completed_by,
        admin_comment: str = "",
    ) -> FileDeletionRequest:
        """
        Complete an approved deletion request.

        Completion applies the requested scope:
            detach_only: deactivate attachment
            archive_file: archive uploaded file
            delete_file: delete file from storage and mark deleted
        """

        if deletion_request.status != DeletionRequestStatus.APPROVED:
            raise FileDeletionError(
                "Only approved deletion requests can be completed."
            )

        if deletion_request.scope == DeletionRequestScope.DETACH_ONLY:
            cls._complete_detach_only(
                deletion_request=deletion_request,
                completed_by=completed_by,
            )
        elif deletion_request.scope == DeletionRequestScope.ARCHIVE_FILE:
            cls._complete_archive_file(
                deletion_request=deletion_request,
            )
        elif deletion_request.scope == DeletionRequestScope.DELETE_FILE:
            cls._complete_delete_file(
                deletion_request=deletion_request,
            )
        else:
            raise FileDeletionError("Unsupported deletion request scope.")

        deletion_request.status = DeletionRequestStatus.COMPLETED
        deletion_request.reviewed_by = completed_by
        deletion_request.completed_at = timezone.now()

        if admin_comment:
            deletion_request.admin_comment = admin_comment

        deletion_request.full_clean()
        deletion_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "completed_at",
                "admin_comment",
                "updated_at",
            ]
        )

        return deletion_request

    @classmethod
    @transaction.atomic
    def cancel_request(
        cls,
        *,
        deletion_request: FileDeletionRequest,
        cancelled_by,
        admin_comment: str = "",
    ) -> FileDeletionRequest:
        """
        Cancel a pending deletion request.
        """

        cls._ensure_pending(deletion_request=deletion_request)

        deletion_request.status = DeletionRequestStatus.CANCELLED
        deletion_request.reviewed_by = cancelled_by
        deletion_request.reviewed_at = timezone.now()
        deletion_request.admin_comment = admin_comment
        deletion_request.full_clean()
        deletion_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "admin_comment",
                "updated_at",
            ]
        )

        return deletion_request

    @staticmethod
    def _ensure_pending(
        *,
        deletion_request: FileDeletionRequest,
    ) -> None:
        """
        Ensure a request is still pending review.
        """

        if deletion_request.status != DeletionRequestStatus.PENDING:
            raise FileDeletionError(
                "Only pending deletion requests can be reviewed."
            )

    @staticmethod
    def _complete_detach_only(
        *,
        deletion_request: FileDeletionRequest,
        completed_by,
    ) -> None:
        """
        Deactivate the attachment only.
        """

        attachment = deletion_request.attachment

        if attachment is None:
            raise FileDeletionError(
                "Detach-only deletion requires an attachment."
            )

        FileAttachmentService.deactivate_attachment(
            attachment=attachment,
            deactivated_by=completed_by,
            reason="Deletion request approved.",
        )

    @staticmethod
    def _complete_archive_file(
        *,
        deletion_request: FileDeletionRequest,
    ) -> None:
        """
        Archive the uploaded file without physical storage deletion.
        """
        if deletion_request.external_link:
            external_link = deletion_request.external_link
            external_link.is_active = False
            external_link.save(update_fields=[
                "is_active",
                "updated_at",
            ])
            return
        
        managed_file = deletion_request.managed_file
        managed_file.lifecycle_status = FileLifecycleStatus.ARCHIVED
        managed_file.full_clean()
        managed_file.save(
            update_fields=[
                "lifecycle_status",
                "updated_at",
            ]
        )

    @staticmethod
    def _complete_delete_file(
        *,
        deletion_request: FileDeletionRequest,
    ) -> None:
        """
        Physically delete the uploaded file from storage.

        Use this sparingly. Most business workflows should archive or
        detach files first because uploaded files may be evidence.
        """
        if deletion_request.external_link:
            external_link = deletion_request.external_link
            external_link.is_active = False
            external_link.save(update_fields=["is_active", "updated_at"])
            return
        
        managed_file = deletion_request.managed_file

        if managed_file.storage_key:
            FileStorageBackend.delete(
                storage_name=managed_file.storage_key,
            )

        managed_file.lifecycle_status = FileLifecycleStatus.DELETED
        managed_file.full_clean()
        managed_file.save(
            update_fields=[
                "lifecycle_status",
                "updated_at",
            ]
        )