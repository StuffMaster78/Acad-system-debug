from decimal import Decimal

from django.db import models


class WriterTrustScore(models.Model):
    """
    Monetization-grade trust score.

    Separate from operational performance metrics.

    Represents:
        "How economically trustworthy is this writer?"
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_trust_scores",
    )

    writer = models.OneToOneField(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="trust_score",
    )

    # ---------------------------------------------------------
    # FINAL TRUST SCORE
    # ---------------------------------------------------------

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Final normalized trust score (0.00 - 100.00).",
    )

    # ---------------------------------------------------------
    # COMPONENT BREAKDOWN
    # Useful for debugging + transparency
    # ---------------------------------------------------------

    rating_component = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    completion_component = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    dispute_component = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    consistency_component = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # ---------------------------------------------------------
    # MARKET RANKING
    # ---------------------------------------------------------

    percentile_rank = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Outperforms X% of writers.",
    )

    tier = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    # ---------------------------------------------------------
    # SOURCE METRICS
    # ---------------------------------------------------------

    source_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    source_review_count = models.PositiveIntegerField(
        default=0,
    )

    source_completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    source_dispute_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # ---------------------------------------------------------
    # SYSTEM
    # ---------------------------------------------------------

    last_event_id = models.UUIDField(
        null=True,
        blank=True,
    )

    correlation_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    recalculated_at = models.DateTimeField(
        auto_now=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Writer Trust Score"
        verbose_name_plural = "Writer Trust Scores"

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(score__gte=Decimal("0.00"))
                    & models.Q(score__lte=Decimal("100.00"))
                ),
                name="writer_trust_score_range",
            ),
        ]

        indexes = [
            models.Index(
                fields=["website", "score"],
                name="trust_site_score_idx",
            ),
            models.Index(
                fields=["website", "percentile_rank"],
                name="trust_percentile_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterTrustScore<writer={self.writer.id}, "
            f"score={self.score}>"
        )