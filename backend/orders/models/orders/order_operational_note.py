from __future__ import annotations

from django.conf import settings
from django.db import models

from websites.models.websites import Website


class OrderOperationalNote(models.Model):
    """
    Staff-only internal note attached to an order.

    Used for operational context, handoff details, and escalation
    notes that are not visible to clients or writers.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_operational_notes",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="operational_notes",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_operational_notes",
    )
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-is_pinned", "-created_at")
        indexes = [
            models.Index(fields=["order", "is_pinned"]),
        ]

    def __str__(self) -> str:
        return f"OperationalNote(order={self.order_id}, author={self.author_id})"
