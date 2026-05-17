from decimal import Decimal

from django.db import models


class WriterReputationBonus(models.Model):
    """
    Immutable reputation reward record.

    Tracks WHY a writer received a trust/reputation bonus.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="reputation_bonuses",
    )

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="reputation_bonuses",
    )

    compensation_event = models.OneToOneField(
        "writer_compensation.CompensationEvent",
        on_delete=models.CASCADE,
        related_name="reputation_bonus",
    )

    trust_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    percentile_rank = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    bonus_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    tier = models.CharField(
        max_length=50,
    )

    review_count = models.PositiveIntegerField(
        default=0,
    )

    average_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    correlation_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    awarded_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Writer Reputation Bonus"
        verbose_name_plural = "Writer Reputation Bonuses"

        indexes = [
            models.Index(
                fields=["writer", "awarded_at"],
                name="rep_bonus_writer_time_idx",
            ),
            models.Index(
                fields=["tier", "awarded_at"],
                name="rep_bonus_tier_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterReputationBonus<writer={self.writer.id}, "
            f"tier={self.tier}>"
        )