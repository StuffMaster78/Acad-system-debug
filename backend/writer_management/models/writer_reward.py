"""
writer_management/models/rewards.py

Writer reward records and admin-defined reward criteria.

TWO MODELS
----------

WriterRewardCriteria
    Admin-defined rules for when a reward is granted.
    Evaluated by reward_evaluation_service against
    WriterPerformanceMetrics (weekly) or WriterPerformance (lifetime).

WriterReward
    A reward granted to a specific writer.
    Created by reward_evaluation_service (auto) or admin (manual).
    Financial disbursement handled by writer_compensation —
    this model is the recognition record only.

WHAT A REWARD IS IN THIS CONTEXT
---------------------------------
A reward is a formal recognition of exceptional performance.
It may or may not carry a financial component (prize_amount).

Examples for an academic writing marketplace:
    - "Top Writer of the Week" — writer with highest composite score
      on the site this week. Prize: $20 bonus.
    - "Perfect Delivery Month" — zero late orders in 30 days,
      min 10 orders completed. Prize: level advancement consideration.
    - "Client Favourite" — 5 consecutive 5-star ratings.
      Prize: featured placement in client assignment browsing.
    - "High Volume Achiever" — 50+ orders completed this month.
      Prize: $50 bonus.

EVALUATION PERIOD
-----------------
WriterRewardCriteria has an evaluation_period field:
    "weekly" — evaluated against WriterPerformanceMetrics
    "monthly" — evaluated against WriterPerformanceSnapshot
    "lifetime" — evaluated against WriterPerformance (lifetime totals)

FINANCIAL DISBURSEMENT
-----------------------
When prize_amount > 0, reward_evaluation_service calls
writer_compensation to credit the writer's wallet.
This model records the recognition event — it does not
hold the financial transaction record.

WHAT WAS FIXED
--------------
- WriterRewardManager deleted (website hack)
- save() Website auto-creation override removed
- awarded_date + created_at merged into awarded_at
- performance_metric + metadata merged into metadata (documented schema)
- prize CharField → prize_description + prize_amount Decimal
- writer.user.username in __str__ fixed
- WriterRewardCriteria gains: is_active, evaluation_period,
  max_lateness_rate, max_revision_rate, prize_amount, prize_description
- WriterReward gains: granted_by, is_auto_awarded
- No auto_reward_enabled on criteria — replaced by is_active
  (simpler: if is_active=True, evaluation service considers it)
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.timezone import now


class WriterRewardCriteria(models.Model):
    """
    Admin-defined criteria for automatic or manual writer rewards.

    Evaluated by reward_evaluation_service on a Celery schedule
    matching the evaluation_period.

    A writer must meet ALL configured thresholds to qualify.
    Null threshold fields are not evaluated (not enforced).

    EVALUATION PERIOD
    -----------------
    weekly → WriterPerformanceMetrics (current week's row)
    monthly → WriterPerformanceSnapshot (current month's row)
    lifetime → WriterPerformance (lifetime totals)
    """

    class EvaluationPeriod(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        LIFETIME = "lifetime", "Lifetime"

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="reward_criteria",
    )
    name = models.CharField(
        max_length=200,
        help_text="Internal name. e.g. 'Top Writer of the Week'.",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Internal description of what this reward recognises.",
    )

    # ----------------------------------------------------------------
    # EVALUATION PERIOD
    # ----------------------------------------------------------------

    evaluation_period = models.CharField(
        max_length=10,
        choices=EvaluationPeriod.choices,
        default=EvaluationPeriod.WEEKLY,
        help_text=(
            "What time window is evaluated. "
            "weekly → WriterPerformanceMetrics. "
            "monthly → WriterPerformanceSnapshot. "
            "lifetime → WriterPerformance."
        ),
    )

    # ----------------------------------------------------------------
    # QUALIFICATION THRESHOLDS
    # All non-null thresholds must be met simultaneously.
    # Null = not enforced for this criteria.
    # ----------------------------------------------------------------

    min_completed_orders = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Minimum orders completed in the evaluation period. "
            "Null = not enforced."
        ),
    )
    min_avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Minimum average rating in the evaluation period. "
            "Range 0.00–5.00. Null = not enforced."
        ),
    )
    min_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Minimum earnings in the evaluation period. "
            "Null = not enforced."
        ),
    )
    min_composite_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Minimum composite performance score. "
            "Null = not enforced."
        ),
    )
    max_lateness_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Maximum acceptable lateness rate (%). "
            "Null = not enforced."
        ),
    )
    max_revision_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Maximum acceptable revision rate (%). "
            "Null = not enforced."
        ),
    )

    # ----------------------------------------------------------------
    # REWARD DEFINITION
    # ----------------------------------------------------------------

    reward_title = models.CharField(
        max_length=200,
        help_text=(
            "Title shown to the writer when reward is granted. "
            "e.g. 'Top Writer of the Week — 14 Jan 2025'."
        ),
    )
    reward_description = models.TextField(
        blank=True,
        default="",
        help_text="What the writer achieved to earn this reward.",
    )
    prize_description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=(
            "Human-readable prize description. "
            "e.g. '$20 bonus credited to wallet'."
        ),
    )
    prize_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Financial value of the reward in platform currency. "
            "0.00 = recognition only, no financial component. "
            "When > 0, reward_evaluation_service calls writer_compensation "
            "to credit the writer's wallet."
        ),
    )

    # ----------------------------------------------------------------
    # STATUS
    # ----------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=(
            "Only active criteria are evaluated by the reward service. "
            "Deactivate instead of deleting to preserve history."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Reward Criteria"
        verbose_name_plural = "Writer Reward Criteria"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(prize_amount__gte=Decimal("0.00")),
                name="reward_criteria_prize_gte_0",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(min_avg_rating__isnull=True) |
                    (
                        models.Q(min_avg_rating__gte=Decimal("0.00")) &
                        models.Q(min_avg_rating__lte=Decimal("5.00"))
                    )
                ),
                name="reward_criteria_rating_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(max_lateness_rate__isnull=True) |
                    (
                        models.Q(max_lateness_rate__gte=Decimal("0.00")) &
                        models.Q(max_lateness_rate__lte=Decimal("100.00"))
                    )
                ),
                name="reward_criteria_lateness_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(max_revision_rate__isnull=True) |
                    (
                        models.Q(max_revision_rate__gte=Decimal("0.00")) &
                        models.Q(max_revision_rate__lte=Decimal("100.00"))
                    )
                ),
                name="reward_criteria_revision_range",
            ),
        ]

    def __str__(self) -> str:
        status = "active" if self.is_active else "inactive"
        return (
            f"WriterRewardCriteria: {self.name} "
            f"[{self.evaluation_period}|{status}]"
        )

    def has_financial_component(self) -> bool:
        """True if this reward carries a monetary prize."""
        return self.prize_amount > Decimal("0.00")


class WriterReward(models.Model):
    """
    A reward granted to a specific writer.

    Append-only — rewards are never deleted or updated.
    The record is permanent even if the criteria is later deactivated.

    Created by:
        reward_evaluation_service (auto-awarded, is_auto_awarded=True)
        Admin via admin API (manual, is_auto_awarded=False)

    Financial disbursement:
        When prize_amount > 0, reward_evaluation_service calls
        writer_compensation.services.bonus_service.credit_bonus()
        BEFORE creating this record (so the compensation record
        exists before the recognition record). If compensation
        fails, this record is not created.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_rewards",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="rewards",
    )
    criteria = models.ForeignKey(
        WriterRewardCriteria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rewards_granted",
        help_text=(
            "Criteria that triggered this reward. "
            "Null for manually granted rewards."
        ),
    )
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_rewards_granted",
        help_text=(
            "Admin who granted the reward. "
            "Null for auto-awarded rewards."
        ),
    )

    # ----------------------------------------------------------------
    # WHAT WAS AWARDED
    # Snapshot of the criteria values at award time.
    # Preserved even if criteria is later edited or deleted.
    # ----------------------------------------------------------------

    title = models.CharField(
        max_length=200,
        help_text="Title shown to the writer.",
    )
    prize_description = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    prize_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Financial value awarded. "
            "0.00 = recognition only."
        ),
    )

    is_auto_awarded = models.BooleanField(
        default=False,
        help_text="True when awarded by reward_evaluation_service.",
    )

    notes = models.TextField(
        blank=True,
        default="",
        help_text="Admin notes on the award.",
    )

    # ----------------------------------------------------------------
    # PERFORMANCE CONTEXT
    # Snapshot of the writer's key metrics at award time.
    # Self-contained audit — does not depend on metrics rows
    # remaining unchanged.
    # ----------------------------------------------------------------

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Performance context at award time. "
            "Schema: {"
            "'evaluation_period': str, "
            "'period_start': 'YYYY-MM-DD', "
            "'period_end': 'YYYY-MM-DD', "
            "'composite_score': float|null, "
            "'avg_rating': float|null, "
            "'completed_orders': int, "
            "'lateness_rate': float|null, "
            "'revision_rate': float|null"
            "}"
        ),
    )

    awarded_at = models.DateTimeField(
        default=now,
        db_index=True,
        help_text="When the reward was granted.",
    )

    class Meta:
        verbose_name = "Writer Reward"
        verbose_name_plural = "Writer Rewards"
        ordering = ["-awarded_at"]
        indexes = [
            models.Index(
                fields=["writer", "awarded_at"],
                name="reward_writer_time_idx",
            ),
            models.Index(
                fields=["website", "awarded_at"],
                name="reward_site_time_idx",
            ),
            models.Index(
                fields=["criteria", "awarded_at"],
                name="reward_criteria_time_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(prize_amount__gte=Decimal("0.00")),
                name="reward_prize_gte_0",
            ),
        ]

    def __str__(self) -> str:
        awarded = "auto" if self.is_auto_awarded else "manual"
        return (
            f"WriterReward<{self.writer.id}> "
            f"{self.title} [{awarded}] "
            f"@ {self.awarded_at:%Y-%m-%d}"
        )

    @property
    def has_financial_component(self) -> bool:
        """True if this reward carried a monetary prize."""
        return self.prize_amount > Decimal("0.00")