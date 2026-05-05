from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from communications.models.audit import CommunicationAuditAction
from communications.models.participant import (
    CommunicationParticipant,
    CommunicationParticipantRole,
)
from communications.services.audit_service import CommunicationAuditService


class CommunicationParticipantService:
    """
    Manage thread participants and access permissions.
    """

    @staticmethod
    @transaction.atomic
    def add_participant(
        *,
        thread,
        user,
        role: str,
        added_by=None,
        can_view: bool = True,
        can_send: bool = True,
        can_upload: bool = True,
        is_observer: bool = False,
    ) -> CommunicationParticipant:
        """
        Add or restore a participant on a thread.
        """
        participant, created = CommunicationParticipant.objects.update_or_create(
            thread=thread,
            user=user,
            defaults={
                "website": thread.website,
                "role": role,
                "can_view": can_view,
                "can_send": can_send,
                "can_upload": can_upload,
                "is_observer": is_observer,
                "added_by": added_by,
                "removed_at": None,
            },
        )

        CommunicationAuditService.log(
            website=thread.website,
            thread=thread,
            actor=added_by,
            action=CommunicationAuditAction.PARTICIPANT_ADDED,
            details={
                "participant_id": participant.pk,
                "user_id": user.id,
                "role": role,
                "created": created,
            },
        )

        return participant

    @staticmethod
    @transaction.atomic
    def remove_participant(
        *,
        thread,
        user,
        removed_by=None,
    ) -> None:
        """
        Remove participant access from a thread.
        """
        CommunicationParticipant.objects.filter(
            thread=thread,
            user=user,
            removed_at__isnull=True,
        ).update(
            can_view=False,
            can_send=False,
            can_upload=False,
            removed_at=timezone.now(),
        )

        CommunicationAuditService.log(
            website=thread.website,
            thread=thread,
            actor=removed_by,
            action=CommunicationAuditAction.PARTICIPANT_REMOVED,
            details={"user_id": user.id},
        )

    @staticmethod
    @transaction.atomic
    def grant_access(
        *,
        participant,
        actor=None,
        can_view: bool = True,
        can_send: bool = True,
        can_upload: bool = True,
    ) -> CommunicationParticipant:
        """
        Grant access permissions to an existing participant.
        """
        participant.can_view = can_view
        participant.can_send = can_send
        participant.can_upload = can_upload
        participant.removed_at = None
        participant.save(
            update_fields=[
                "can_view",
                "can_send",
                "can_upload",
                "removed_at",
            ],
        )

        CommunicationAuditService.log(
            website=participant.website,
            thread=participant.thread,
            actor=actor,
            action=CommunicationAuditAction.PARTICIPANT_ADDED,
            details={
                "participant_id": participant.id,
                "user_id": participant.user_id,
                "permissions": {
                    "can_view": can_view,
                    "can_send": can_send,
                    "can_upload": can_upload,
                },
            },
        )

        return participant

    @staticmethod
    @transaction.atomic
    def reassign_writer(
        *,
        thread,
        old_writer,
        new_writer,
        actor=None,
    ) -> CommunicationParticipant:
        """
        Replace the current writer while preserving thread history.

        The new writer can view previous context.
        The old writer loses future access.
        """
        if old_writer is not None:
            CommunicationParticipantService.remove_participant(
                thread=thread,
                user=old_writer,
                removed_by=actor,
            )

        return CommunicationParticipantService.add_participant(
            thread=thread,
            user=new_writer,
            role=CommunicationParticipantRole.WRITER,
            added_by=actor,
            can_view=True,
            can_send=True,
            can_upload=True,
        )