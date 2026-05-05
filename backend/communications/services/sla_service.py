from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from communications.models.sla import CommunicationThreadSLA


class CommunicationThreadSLAService:
    """
    Manage response tracking for communication threads.
    """

    DEFAULT_FIRST_RESPONSE_MINUTES = 30
    DEFAULT_NEXT_RESPONSE_MINUTES = 60

    @staticmethod
    def ensure_for_thread(*, thread) -> CommunicationThreadSLA:
        """
        Ensure a thread has an SLA record.
        """
        sla, _ = CommunicationThreadSLA.objects.get_or_create(
            website=thread.website,
            thread=thread,
        )
        return sla

    @staticmethod
    @transaction.atomic
    def start(
        *,
        thread,
        first_response_minutes: int | None = None,
    ) -> CommunicationThreadSLA:
        """
        Start first response tracking.
        """
        minutes = (
            first_response_minutes
            or CommunicationThreadSLAService.DEFAULT_FIRST_RESPONSE_MINUTES
        )
        now = timezone.now()
        sla = CommunicationThreadSLAService.ensure_for_thread(thread=thread)

        sla.first_response_due_at = now + timedelta(minutes=minutes)
        sla.next_response_due_at = sla.first_response_due_at
        sla.is_breached = False
        sla.breached_at = None
        sla.save(
            update_fields=[
                "first_response_due_at",
                "next_response_due_at",
                "is_breached",
                "breached_at",
            ],
        )

        return sla

    @staticmethod
    @transaction.atomic
    def update_on_message(
        *,
        thread,
        sender_role: str,
        next_response_minutes: int | None = None,
    ) -> CommunicationThreadSLA:
        """
        Update SLA timestamps when a message is sent.
        """
        minutes = (
            next_response_minutes
            or CommunicationThreadSLAService.DEFAULT_NEXT_RESPONSE_MINUTES
        )
        now = timezone.now()
        sla = CommunicationThreadSLAService.ensure_for_thread(thread=thread)

        if sender_role == "client":
            sla.last_client_response_at = now
            sla.next_response_due_at = now + timedelta(minutes=minutes)

        if sender_role == "writer":
            sla.last_writer_response_at = now
            sla.next_response_due_at = now + timedelta(minutes=minutes)

        if sender_role in {"admin", "superadmin", "support"}:
            sla.last_staff_response_at = now
            sla.next_response_due_at = None
            sla.first_response_due_at = None

        sla.is_breached = False
        sla.breached_at = None
        sla.save(
            update_fields=[
                "last_client_response_at",
                "last_writer_response_at",
                "last_staff_response_at",
                "next_response_due_at",
                "first_response_due_at",
                "is_breached",
                "breached_at",
            ],
        )

        return sla

    @staticmethod
    @transaction.atomic
    def mark_breached(*, sla) -> CommunicationThreadSLA:
        """
        Mark an SLA as breached.
        """
        sla.is_breached = True
        sla.breached_at = timezone.now()
        sla.save(update_fields=["is_breached", "breached_at"])
        return sla