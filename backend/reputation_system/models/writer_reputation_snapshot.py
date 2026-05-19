from __future__ import annotations

from decimal import Decimal

from django.db import models


class WriterReputationSnapshot(models.Model):
    """
    Canonical aggregated trust state for a writer.

    This is NOT merely a ratings cache.

    This model powers:
        - writer trust scoring
        - marketplace ranking
        - compensation incentives
        - reward qualification
        - admin trust analytics
    """
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_reputation_snapshots",
    )

    writer_id = models.UUIDField(
        unique=True,
        db_index=True,
    )

    # CORE REVIEW SIGNALS

    rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    review_count = models.PositiveIntegerField(
        default=0,
    )

    verified_review_count = models.PositiveIntegerField(
        default=0,
    )
    # For richer competitive metrics
    metadata = models.JSONField(default=dict, blank=True)

    # TRUST ENGINE

    trust_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Composite trust score derived from reputation, "
            "performance quality, consistency, and penalties."
        ),
        db_index=True,
    )

    percentile_rank = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Outperforms X% of writers.",
    )

    consistency_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Measures rating stability over time."
        ),
    )

    rating_velocity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Recent reputation momentum.",
    )

    # RISK PENALTIES

    dispute_penalty_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    revision_penalty_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    cancellation_penalty_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    moderation_penalty_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # REWARD STATE

    qualifies_for_bonus = models.BooleanField(
        default=False,
    )
    bonus_eligibility_reason = models.CharField(
        max_length=255,
        blank=True,
    )
    last_bonus_qualified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Rich competitive metrics
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Precomputed reputation intelligence. "
            "Used for rewards, routing, "
            "leaderboards, and analytics."
        ),
    )
    # Snapshot Timing
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-trust_score"]
        indexes = [
            models.Index(
                fields=["trust_score"],
                name="writer_rep_trust_idx",
            ),
            models.Index(
                fields=["percentile_rank"],
                name="writer_rep_percentile_idx",
            ),
            models.Index(
                fields=["qualifies_for_bonus"],
                name="writer_rep_bonus_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(rating__gte=Decimal("0.00")) &
                    models.Q(rating__lte=Decimal("5.00"))
                ),
                name="writer_rep_rating_range",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(percentile_rank__gte=Decimal("0.00")) &
                    models.Q(percentile_rank__lte=Decimal("100.00"))
                ),
                name="writer_rep_percentile_range",
            ),
            models.CheckConstraint(
                check=models.Q(trust_score__gte=Decimal("0.00")),
                name="writer_rep_trust_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterReputationSnapshot<"
            f"{self.writer_id}:{self.trust_score}"
            f">"
        )
    
    @property
    def is_elite_writer(self) -> bool:
        """
        High-trust marketplace writers.
        """
        return self.percentile_rank >= Decimal("90.00")

    @property
    def has_strong_reputation(self) -> bool:
        return self.trust_score >= Decimal("80.00")