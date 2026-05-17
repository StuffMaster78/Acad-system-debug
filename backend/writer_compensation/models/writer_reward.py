from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone

from websites.models.websites import Website
from writer_management.models.writer_profile import WriterProfile


class WriterReward(models.Model):
    """
    Immutable reward issuance record.

    One row = one reward granted to one writer.

    DOMAIN ROLE
    -----------
    Business/audit/gamification layer.

    CompensationEvent answers:
        "What changed financially?"

    WriterReward answers:
        "Why was the writer rewarded?"

    IMPORTANT
    ----------
    This is NOT a financial ledger.
    CompensationEvent remains the source of truth for money.

    This model exists for:
        - reward history
        - writer achievement timelines
        - analytics
        - qualification audits
        - anti-duplication protection
        - trust/routing systems
        - future gamification
    """

    class RewardStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ISSUED = "ISSUED", "Issued"
        REVOKED = "REVOKED", "Revoked"
        FAILED = "FAILED", "Failed"

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_rewards",
    )

    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="rewards",
    )

    reward_rule = models.ForeignKey(
        "writer_compensation.RewardRule",
        on_delete=models.PROTECT,
        related_name="issued_rewards",
    )

    # ---------------------------------------------------------
    # OPTIONAL FINANCIAL LINK
    # Not all rewards are monetary.
    # ---------------------------------------------------------

    compensation_event = models.OneToOneField(
        "writer_compensation.CompensationEvent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_reward",
    )

    status = models.CharField(
        max_length=20,
        choices=RewardStatus.choices,
        default=RewardStatus.PENDING,
        db_index=True,
    )

    # ---------------------------------------------------------
    # QUALIFICATION SNAPSHOT
    # Immutable evidence of qualification state at issuance.
    # ---------------------------------------------------------

    average_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    percentile_rank = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="0.00–100.00",
    )

    trust_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    composite_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    completed_orders = models.PositiveIntegerField(
        default=0,
    )

    review_count = models.PositiveIntegerField(
        default=0,
    )

    # ---------------------------------------------------------
    # REWARD SNAPSHOT
    # Freeze issued values even if RewardRule later changes.
    # ---------------------------------------------------------

    reward_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    trust_score_bonus = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    badge_name = models.CharField(
        max_length=120,
        blank=True,
    )

    reward_title = models.CharField(
        max_length=255,
    )

    reward_description = models.TextField(
        blank=True,
    )

    # ---------------------------------------------------------
    # PERIOD CONTEXT
    # ---------------------------------------------------------

    period_start = models.DateField(
        null=True,
        blank=True,
    )

    period_end = models.DateField(
        null=True,
        blank=True,
    )

    # ---------------------------------------------------------
    # SYSTEM METADATA
    # ---------------------------------------------------------

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    issued_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-issued_at"]

        indexes = [
            models.Index(
                fields=["website", "writer"],
                name="writer_reward_writer_idx",
            ),
            models.Index(
                fields=["website", "status"],
                name="writer_reward_status_idx",
            ),
            models.Index(
                fields=["writer", "issued_at"],
                name="writer_reward_timeline_idx",
            ),
            models.Index(
                fields=["reward_rule", "issued_at"],
                name="writer_reward_rule_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    reward_amount__gte=Decimal("0.00")
                ),
                name="writer_reward_amount_gte_0",
            ),

            models.CheckConstraint(
                condition=(
                    models.Q(
                        average_rating__isnull=True
                    )
                    | (
                        models.Q(
                            average_rating__gte=Decimal("0.00")
                        )
                        & models.Q(
                            average_rating__lte=Decimal("5.00")
                        )
                    )
                ),
                name="writer_reward_avg_rating_range",
            ),

            models.CheckConstraint(
                condition=(
                    models.Q(
                        percentile_rank__isnull=True
                    )
                    | (
                        models.Q(
                            percentile_rank__gte=Decimal("0.00")
                        )
                        & models.Q(
                            percentile_rank__lte=Decimal("100.00")
                        )
                    )
                ),
                name="writer_reward_percentile_range",
            ),

            models.CheckConstraint(
                condition=(
                    models.Q(
                        composite_score__isnull=True
                    )
                    | models.Q(
                        composite_score__gte=Decimal("0.00")
                    )
                ),
                name="writer_reward_composite_score_gte_0",
            ),

            models.CheckConstraint(
                condition=(
                    models.Q(period_start__isnull=True)
                    | models.Q(period_end__isnull=True)
                    | models.Q(
                        period_end__gte=models.F("period_start")
                    )
                ),
                name="writer_reward_period_valid",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.writer.registration_id} | "
            f"{self.reward_title}"
        )

    @property
    def is_financial_reward(self) -> bool:
        return self.reward_amount > Decimal("0.00")

    @property
    def has_badge(self) -> bool:
        return bool(self.badge_name)

    @property
    def was_revoked(self) -> bool:
        return (
            self.status
            == self.RewardStatus.REVOKED
        )