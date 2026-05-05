from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from communications.models.audit import CommunicationAuditAction
from communications.models.edit import CommunicationMessageEdit
from communications.services.audit_service import CommunicationAuditService
from communications.validators import CommunicationMessageValidator


class CommunicationMessageEditService:
    """
    Edit messages while preserving history.
    """

    @staticmethod
    @transaction.atomic
    def edit_message(
        *,
        message,
        new_body: str,
        edited_by,
    ):
        """
        Edit a message and store the previous body.
        """
        previous_body = message.body
        CommunicationMessageValidator.validate_can_edit(message=message)
        CommunicationMessageValidator.validate_body(body=new_body)

        edit = CommunicationMessageEdit.objects.create(
            website=message.website,
            thread=message.thread,
            message=message,
            edited_by=edited_by,
            previous_body=previous_body,
            new_body=new_body,
        )

        message.body = new_body
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save(update_fields=[
            "body",
            "is_edited",
            "edited_at",
            "updated_at"
        ])

        CommunicationAuditService.log(
            website=message.website,
            thread=message.thread,
            message=message,
            actor=edited_by,
            action=CommunicationAuditAction.MESSAGE_EDITED,
            details={"edit_id": edit.pk},
        )

        return message