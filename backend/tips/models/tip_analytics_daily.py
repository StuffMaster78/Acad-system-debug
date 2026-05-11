from django.db import models
from django.utils import timezone


class TipAnalyticsDaily(models.Model):
    """
    Pre-aggregated analytics snapshot.

    This avoids heavy runtime aggregation.
    """

    date = models.DateField(db_index=True)

    total_tips = models.PositiveIntegerField(default=0)

    total_successful_tips = models.PositiveIntegerField(default=0)

    total_failed_tips = models.PositiveIntegerField(default=0)

    total_volume_cents = models.BigIntegerField(default=0)

    writer_earnings_cents = models.BigIntegerField(default=0)

    platform_fee_cents = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date",)