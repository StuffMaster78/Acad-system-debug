from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.enums import FilePurpose, FileVisibility
from files_management.models import FileAttachment
from files_management.services import (
    FileAttachmentService,
    FileUploadService,
)


class MessageFileIntegrationService:
    """
    Messaging-facing integration for message attachments.

    The messaging app must validate conversation membership before
    calling this service. This service only stores and attaches files.
    """

    @classmethod
    @transaction.atomic
    def attach_message_file(
        cls,
        *,
        message,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        managed_file = FileUploadService.upload_file(
            website=message.website,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.MESSAGE_ATTACHMENT,
            is_public=False,
        )

        return FileAttachmentService.attach_managed_file(
            website=message.website,
            obj=message,
            managed_file=managed_file,
            purpose=FilePurpose.MESSAGE_ATTACHMENT,
            visibility=FileVisibility.CONVERSATION_PARTICIPANTS,
            attached_by=uploaded_by,
        )