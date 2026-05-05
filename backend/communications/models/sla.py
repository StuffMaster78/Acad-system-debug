from __future__ import annotations

from django.db import models


class CommunicationThreadSLA(models.Model):
    """
    Response tracking for prompt communication.

    This supports inbox labels like client waiting, overdue, and needs
    staff reply without requiring realtime messaging.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_thread_slas",
    )
    thread = models.OneToOneField(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="sla",
    )

    first_response_due_at = models.DateTimeField(null=True, blank=True)
    next_response_due_at = models.DateTimeField(null=True, blank=True)

    last_client_response_at = models.DateTimeField(null=True, blank=True)
    last_writer_response_at = models.DateTimeField(null=True, blank=True)
    last_staff_response_at = models.DateTimeField(null=True, blank=True)

    is_breached = models.BooleanField(default=False)
    breached_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "is_breached"]),
            models.Index(fields=["website", "next_response_due_at"]),
            models.Index(fields=["website", "first_response_due_at"]),
        ]

    def __str__(self) -> str:
        return f"SLA for thread {self.thread.pk}"