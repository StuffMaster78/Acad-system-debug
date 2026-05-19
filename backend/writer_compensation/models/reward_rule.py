from __future__ import annotations

from decimal import Decimal

from django.db import models

from websites.models.websites import Website


class RewardRule(models.Model):
    """
    
    Declarative reward criteria.

    Admin-configurable.
    Evaluated by reward evaluation services.

    Examples:
        - avg_rating >= 4.80
        - percentile_rank >= 90
        - review_count >= 15
        - trust_score >= 85

    IMPORTANT
    ----------
    This model defines eligibility only.

    It does NOT:
        - calculate rankings
        - create bonuses
        - pay writers

    Reward issuance happens through:
        reward_evaluation_service
            -> EventIntakeService.record(...)
    """

    class RuleType(models.TextChoices):
        WEEKLY = "WEEKLY", "Weekly"
        MONTHLY = "MONTHLY", "Monthly"
        LIFETIME = "LIFETIME", "Lifetime"

    class RewardType(models.TextChoices):
        CASH_BONUS = "CASH_BONUS", "Cash Bonus"
        BADGE = "BADGE", "Badge"
        PRIORITY_ROUTING = "PRIORITY_ROUTING", "Priority Routing"
        TRUST_SCORE_BOOST = "TRUST_SCORE_BOOST", "Trust Score Boost"

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="reward_rules",
    )

    name = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        max_length=120,
    )

    description = models.TextField(
        blank=True,
    )

    rule_type = models.CharField(
        max_length=20,
        choices=RuleType.choices,
        db_index=True,
    )

    reward_type = models.CharField(
        max_length=30,
        choices=RewardType.choices,
    )

    # ---------------------------------------------------------
    # ELIGIBILITY THRESHOLDS
    # Null = ignored
    # ---------------------------------------------------------

    minimum_avg_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    minimum_review_count = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    minimum_percentile_rank = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="0.00–100.00",
    )

    minimum_trust_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    minimum_completed_orders = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    maximum_lateness_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    maximum_dispute_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # ---------------------------------------------------------
    # REWARD OUTPUT
    # ---------------------------------------------------------

    reward_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    trust_score_bonus = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    badge_name = models.CharField(
        max_length=120,
        blank=True,
    )

    priority_boost_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
    )

    # ---------------------------------------------------------
    # SAFETY
    # ---------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    is_repeatable = models.BooleanField(
        default=False,
        help_text=(
            "If False, writer can only receive this reward once."
        ),
    )
    cooldown_days = models.PositiveIntegerField(
        default=0,
    )
    max_rewards_per_period = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "slug"],
                name="unique_reward_rule_slug_per_website",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(reward_amount__gte=Decimal("0.00"))
                ),
                name="reward_rule_reward_amount_gte_0",
            ),

            models.CheckConstraint(
                check=(
                    models.Q(minimum_avg_rating__isnull=True)
                    | (
                        models.Q(minimum_avg_rating__gte=Decimal("0.00"))
                        & models.Q(minimum_avg_rating__lte=Decimal("5.00"))
                    )
                ),
                name="reward_rule_avg_rating_range",
            ),

            models.CheckConstraint(
                check=(
                    models.Q(minimum_percentile_rank__isnull=True)
                    | (
                        models.Q(minimum_percentile_rank__gte=Decimal("0.00"))
                        & models.Q(minimum_percentile_rank__lte=Decimal("100.00"))
                    )
                ),
                name="reward_rule_percentile_range",
            ),
        ]
        indexes = [
            models.Index(
                fields=["website", "is_active"],
                name="reward_rule_active_idx",
            ),
            models.Index(
                fields=["website", "rule_type", "is_active"],
                name="reward_rule_type_active_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.rule_type})"


    @property
    def is_bonus_rule(self) -> bool:
        return (
            self.reward_type
            == self.RewardType.CASH_BONUS
        )

    @property
    def grants_priority_routing(self) -> bool:
        return (
            self.reward_type
            == self.RewardType.PRIORITY_ROUTING
        )

    @property
    def grants_badge(self) -> bool:
        return (
            self.reward_type
            == self.RewardType.BADGE
        )