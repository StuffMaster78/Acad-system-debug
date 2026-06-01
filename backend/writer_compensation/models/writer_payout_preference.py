from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from writer_compensation.enums.compensation_enums import (
    WindowType,
)

User = settings.AUTH_USER_MODEL


class WriterPayoutPreference(models.Model):
    """
    One record per writer per website. Stores the writer's chosen payout cycle.

    Once set, the cycle is locked. The writer must submit a CycleChangeRequest
    for admin approval. Changes take effect only at the start of the next window
    after approval — never mid-cycle.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.PROTECT,
        related_name="writer_payout_preferences",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.PROTECT,
        related_name="payout_preferences",
    )
    cycle_type = models.CharField(
        max_length=16,
        choices=WindowType.choices,
    )
    locked = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        unique_together = [("website", "writer")]

    def __str__(self) -> str:
        return f"{self.writer.pk} | {self.website.pk} | {self.cycle_type}"