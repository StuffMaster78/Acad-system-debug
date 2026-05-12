from __future__ import annotations

from django.db import models

from websites.models.websites import Website


class CompensationEventLink(models.Model):
    """
    Universal mapping layer between CompensationEvent and domain objects.

    This prevents duplication chaos and gives a single trace path:
        Order / Class / SpecialOrder / Tip / Bonus / Fine
        → FinancialEvent
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="compensation_event_links",
    )

    financial_event = models.ForeignKey(
        "writer_compensation.CompensationEvent",
        on_delete=models.CASCADE,
        related_name="links",
    )

    # Generic linking (keeps system extensible)
    content_type = models.CharField(max_length=64)
    object_id = models.CharField(max_length=64)

    event_role = models.CharField(
        max_length=32,
        help_text="e.g ORDER_EARNING, TIP, BONUS, FINE, REVERSAL",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["financial_event"]),
        ]