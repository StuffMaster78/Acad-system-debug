from __future__ import annotations

from django.db import transaction

from communications.constants import CommunicationThreadKind
from communications.services.audit_service import CommunicationAuditService
from communications.services.event_recipient_service import (
    CommunicationEventRecipientService,
)
from communications.services.event_service import CommunicationEventService
from communications.services.participant_service import (
    CommunicationParticipantService,
)
from communications.services.message_service import CommunicationMessageService

class CommunicationParticipantSyncService:
    """
    Synchronize participants based on domain changes.
    """

    WRITER_RELEVANT_THREAD_KINDS = {
        CommunicationThreadKind.CLIENT_WRITER,
        CommunicationThreadKind.WRITER_SUPPORT,
    }

    @staticmethod
    @transaction.atomic
    def sync_writer(
        *,
        threads,
        new_writer,
        old_writer=None,
        actor=None,
    ) -> None:
        """
        Sync writer participant across relevant threads.

        Supports:
            1. Initial assignment.
            2. Reassignment.
            3. Writer removal.

        The new writer can view previous context.
        The old writer loses future access.

        Args:
            threads: queryset or list of CommunicationThread
            new_writer: user instance
            old_writer: user instance or None
            actor: user performing the change
        """
        for thread in threads:
            if thread.kind not in (
                CommunicationParticipantSyncService.WRITER_RELEVANT_THREAD_KINDS
            ):
                continue

            # Remove old writer
            if old_writer is not None:
                CommunicationParticipantService.remove_participant(
                    thread=thread,
                    user=old_writer,
                    removed_by=actor,
                )

            # Add new writer
            if new_writer is not None:
                CommunicationParticipantService.add_participant(
                    thread=thread,
                    user=new_writer,
                    role="writer",
                    added_by=actor,
                    can_view=True,
                    can_send=True,
                )

            CommunicationMessageService.create_system_message(
                thread=thread,
                body=CommunicationParticipantSyncService._writer_sync_message(
                    new_writer=new_writer,
                    old_writer=old_writer,
                ),
                metadata={
                    "event": "writer_synced",
                    "new_writer_id": (
                        new_writer.pk if new_writer is not None else None
                    ),
                    "old_writer_id": (
                        old_writer.pk if old_writer is not None else None
                    ),
                },
            )

            CommunicationAuditService.log(
                website=thread.website,
                thread=thread,
                actor=actor,
                action="thread.writer.synced",
                details={
                    "new_writer_id": new_writer.pk,
                    "old_writer_id": (
                        old_writer.pk if old_writer else None
                    ),
                },
            )

            recipient_ids = (
                    CommunicationEventRecipientService.active_thread_participant_ids(
                        thread=thread,
                    )
            )

            transaction.on_commit(
                        lambda thread=thread, recipient_ids=recipient_ids: (
                            CommunicationEventService.thread_updated(
                                thread=thread,
                                recipient_user_ids=recipient_ids,
                            )
                        ),
                    )

    @staticmethod
    def _writer_sync_message(*, new_writer=None, old_writer=None) -> str:
        """
        Return system message body for writer assignment changes.
        """
        if old_writer is None and new_writer is not None:
            new_writer_label = CommunicationParticipantSyncService._user_label(
                user=new_writer,
            )
            return f"Writer assigned: {new_writer_label}."

        if old_writer is not None and new_writer is not None:
            old_writer_label = CommunicationParticipantSyncService._user_label(
                user=old_writer,
            )
            new_writer_label = CommunicationParticipantSyncService._user_label(
                user=new_writer,
            )
            return (
                f"Writer reassigned from {old_writer_label} "
                f"to {new_writer_label}."
            )

        if old_writer is not None and new_writer is None:
            old_writer_label = CommunicationParticipantSyncService._user_label(
                user=old_writer,
            )
            return f"Writer removed: {old_writer_label}."

        return "Writer assignment updated."

    @staticmethod
    def _user_label(*, user) -> str:
        """
        Return safe user label.
        """
        if hasattr(user, "get_full_name"):
            full_name = user.get_full_name()
            if full_name:
                return full_name

        return getattr(user, "email", str(user))

