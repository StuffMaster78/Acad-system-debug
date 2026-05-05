from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.db import transaction

from communications.models.attachment import CommunicationAttachment
from communications.models.audit import CommunicationAuditAction
from communications.selectors.policy_selectors import (
    CommunicationThreadPolicySelector,
)
from communications.services.audit_service import CommunicationAuditService
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)

from communications.services.event_recipient_service import (
    CommunicationEventRecipientService,
)
from communications.services.event_service import CommunicationEventService


class CommunicationAttachmentService:
    """
    Bridge communication messages to files_management.
    """

    @staticmethod
    @transaction.atomic
    def attach_file(
        *,
        message,
        file,
        uploaded_by,
        requires_moderation: bool | None = None,
    ) -> CommunicationAttachment:
        """
        Attach an existing managed file to a message.
        """
        thread = message.thread

        CommunicationThreadGuardService.enforce_can_send_message(
            user=uploaded_by,
            website=message.website,
            thread=thread,
        )

        policy = CommunicationThreadPolicySelector.get_for_kind(
            website=message.website,
            thread_kind=thread.kind,
        )

        if policy is not None and not policy.allow_attachments:
            raise PermissionDenied("Attachments are not allowed in this thread.")

        should_moderate = bool(
            requires_moderation
            or (
                policy is not None
                and policy.require_attachment_moderation
            )
        )

        attachment = CommunicationAttachment.objects.create(
            website=message.website,
            thread=thread,
            message=message,
            file=file,
            uploaded_by=uploaded_by,
            requires_moderation=should_moderate,
            is_visible=not should_moderate,
        )

        recipient_user_ids = (
            CommunicationEventRecipientService.active_thread_participant_ids(
                thread=thread,
                exclude_user=uploaded_by,
            )
        )

        transaction.on_commit(
            lambda: CommunicationEventService.attachment_added(
                attachment=attachment,
                recipient_user_ids=recipient_user_ids,
            ),
        )

        CommunicationAuditService.log(
            website=message.website,
            thread=thread,
            message=message,
            actor=uploaded_by,
            action=CommunicationAuditAction.ATTACHMENT_ADDED,
            details={
                "attachment_id": attachment.pk,
                "file_id": file.id,
                "requires_moderation": should_moderate,
            },
        )

        return attachment

    @staticmethod
    @transaction.atomic
    def hide_attachment(
        *,
        attachment,
        actor,
        reason: str = "",
    ) -> CommunicationAttachment:
        """
        Hide an attachment from users.
        """
        attachment.is_visible = False
        attachment.save(update_fields=["is_visible"])

        CommunicationAuditService.log(
            website=attachment.website,
            thread=attachment.thread,
            message=attachment.message,
            actor=actor,
            action=CommunicationAuditAction.ATTACHMENT_HIDDEN,
            details={
                "attachment_id": attachment.id,
                "reason": reason,
            },
        )

        return attachment