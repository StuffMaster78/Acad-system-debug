from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from communications.models.participant import CommunicationParticipant
from communications.models.thread import CommunicationThread
from communications.services.audit_service import CommunicationAuditService
from communications.services.event_service import CommunicationEventService
from communications.services.event_recipient_service import (
    CommunicationEventRecipientService,
)
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)
from communications.integrations.registry import (
    CommunicationAdapterRegistry,
)


class CommunicationThreadService:
    """
    Create and manage communication threads.
    """

    @staticmethod
    @transaction.atomic
    def create_thread(
        *,
        target,
        thread_kind: str,
        created_by,
        website=None,
    ) -> CommunicationThread:
        """
        Create a communication thread for a domain object.
        """
        adapter = CommunicationAdapterRegistry.get_adapter(target=target)

        context = adapter.get_context(target=target)

        resolved_website = website or context.website

        access = adapter.user_can_access_target(
            user=created_by,
            target=target,
        )

        if not access.allowed:
            raise PermissionError(access.reason)

        content_type = ContentType.objects.get_for_model(target)

        thread = CommunicationThread.objects.create(
            website=resolved_website,
            target_content_type=content_type,
            target_object_id=target.pk,
            kind=thread_kind,
            created_by=created_by,
        )

        participants = adapter.get_default_participants(
            target=target,
            thread_kind=thread_kind,
        )

        for user in participants:
            CommunicationParticipant.objects.get_or_create(
                website=resolved_website,
                thread=thread,
                user=user,
                defaults={
                    "added_by": created_by,
                    "can_view": True,
                    "can_send": True,
                },
            )

        CommunicationAuditService.log(
            website=resolved_website,
            thread=thread,
            actor=created_by,
            action="thread.created",
            details={
                "thread_kind": thread_kind,
                "target_id": target.pk,
            },
        )

        recipient_ids = (
            CommunicationEventRecipientService.active_thread_participant_ids(
                thread=thread,
            )
        )

        transaction.on_commit(
            lambda: CommunicationEventService.thread_updated(
                thread=thread,
                recipient_user_ids=recipient_ids,
            ),
        )

        return thread
    

    @staticmethod
    @transaction.atomic
    def get_or_create_thread(
        *,
        target,
        thread_kind: str,
        created_by,
        website=None,
    ) -> CommunicationThread:
        """
        Return existing thread or create it.
        """
        adapter = CommunicationAdapterRegistry.get_adapter(target=target)
        context = adapter.get_context(target=target)
        resolved_website = website or context.website

        content_type = ContentType.objects.get_for_model(target)

        thread = CommunicationThread.objects.filter(
            website=resolved_website,
            target_content_type=content_type,
            target_object_id=target.pk,
            kind=thread_kind,
        ).first()

        if thread is not None:
            return thread

        return CommunicationThreadService.create_thread(
            target=target,
            thread_kind=thread_kind,
            created_by=created_by,
            website=resolved_website,
        )