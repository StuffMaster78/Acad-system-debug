from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from websites.models.websites import Website


class OrderDisputeWriterResponse(models.Model):
    """
    Writer's formal response to a dispute raised against their order.

    A writer may only submit one response per dispute. Staff can view
    this alongside the dispute when deciding resolution.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="dispute_writer_responses",
    )
    dispute = models.OneToOneField(
        "orders.OrderDispute",
        on_delete=models.CASCADE,
        related_name="writer_response",
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dispute_responses",
        limit_choices_to={"role": "writer"},
    )
    response_text = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"WriterResponse dispute={self.dispute_id} writer={self.writer_id}"
