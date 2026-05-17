from __future__ import annotations

from decimal import Decimal

from django.db import models

from websites.models.websites import Website


class ReputationReward(models.Model):
    """
    Immutable reward record generated from reputation/trust performance.

    This is the business-layer reward object.

    CompensationEvent remains the financial truth layer.
    ReputationReward explains WHY the reward existed.

    Example:
        "Writer outperformed 92% of writers this week."
        "Average rating exceeded 4.85 threshold."

    One reward may generate one CompensationEvent.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="reputation_rewards",
    )

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="reputation_rewards",
    )

    performance_snapshot = models.ForeignKey(
        "writer_management.WriterPerformanceSnapshot",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reputation_rewards",
    )

    performance_metrics = models.ForeignKey(
        "writer_management.WriterPerformanceMetrics",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reputation_rewards",
    )

    compensation_event = models.OneToOneField(
        "writer_compensation.CompensationEvent",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reputation_reward",
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    reward_reason = models.CharField(
        max_length=120,
        db_index=True,
        help_text=(
            "Semantic reward category. "
            "Examples: HIGH_RATING, TOP_PERCENTILE, "
            "CONSISTENCY_STREAK, TRUST_SCORE."
        ),
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    percentile_rank = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Writer outperformed X% of writers.",
    )

    average_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    trust_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    awarded_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-awarded_at"]
        indexes = [
            models.Index(
                fields=["website", "writer"],
                name="rep_reward_site_writer_idx",
            ),
            models.Index(
                fields=["reward_reason", "awarded_at"],
                name="rep_reward_reason_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=Decimal("0.00")),
                name="rep_reward_amount_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"ReputationReward<{self.writer.id}> "
            f"{self.reward_reason} "
            f"{self.amount}"
        )