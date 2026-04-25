from __future__ import annotations

from django.db import models


class OrderDraft(models.Model):
    """
    Draft submission tied to milestone or manual request.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="drafts",
    )
    milestone = models.ForeignKey(
        "orders.OrderMilestone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="drafts",
    )

    submitted_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
    )

    status = models.CharField(
        max_length=32,
        default="submitted",
    )

    note = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)