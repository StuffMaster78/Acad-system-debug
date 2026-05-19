from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.enums import FilePurpose, FileVisibility
from files_management.integrations.messages import MessageFileIntegrationService
from files_management.models import FileAttachment
from files_management.services import FileAttachmentService, FileUploadService

from tickets.constants import TicketAction
from tickets.services.ticket_log_service import TicketLogService


class TicketFileService:
    """
    Bridge ticket uploads to central files_management.
    """

    @classmethod
    @transaction.atomic
    def attach_ticket_file(
        cls,
        *,
        ticket,
        uploaded_by,
        uploaded_file: UploadedFile,
        message=None,
        is_internal: bool = False,
        metadata: dict | None = None,
    ) -> FileAttachment:
        if message is not None:
            attachment = MessageFileIntegrationService.attach_message_file(
                message=message,
                uploaded_by=uploaded_by,
                uploaded_file=uploaded_file,
            )
        else:
            managed_file = FileUploadService.upload_file(
                website=ticket.website,
                uploaded_by=uploaded_by,
                uploaded_file=uploaded_file,
                purpose=FilePurpose.SUPPORT_ATTACHMENT,
                is_public=False,
            )
            attachment = FileAttachmentService.attach_managed_file(
                website=ticket.website,
                obj=ticket,
                managed_file=managed_file,
                purpose=FilePurpose.SUPPORT_ATTACHMENT,
                visibility=(
                    FileVisibility.INTERNAL_ONLY
                    if is_internal
                    else FileVisibility.CONVERSATION_PARTICIPANTS
                ),
                attached_by=uploaded_by,
                metadata={
                    "ticket_id": ticket.id,
                    "is_internal": is_internal,
                    **(metadata or {}),
                },
            )

        TicketLogService.record(
            ticket=ticket,
            actor=uploaded_by,
            action=TicketAction.FILE_ATTACHED,
            metadata={"file_attachment_id": attachment.id},
        )
        return attachment
