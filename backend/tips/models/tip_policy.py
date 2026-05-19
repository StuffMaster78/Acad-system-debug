from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class TipPolicy(models.Model):
    """
    Runtime-configurable tipping policy.

    This model governs how the tipping system behaves at runtime,
    including:
    - financial split configuration
    - moderation thresholds
    - operational feature toggles
    - fraud/risk controls

    Historical correctness must NEVER rely on this model directly.
    Settlement snapshots should persist immutable policy state at the
    time a tip is processed.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    writer_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        help_text=(
            "Percentage of the tip allocated to the writer."
        ),
    )

    platform_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        help_text=(
            "Percentage of the tip retained by the platform."
        ),
    )

    minimum_tip_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
        help_text=(
            "Minimum allowable tip amount in USD."
        ),
    )

    risk_review_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1000.00"),
        validators=[
            MinValueValidator(Decimal("1.00")),
        ],
        help_text=(
            "Tips above this amount may be flagged for review."
        ),
    )

    allow_wallet_tips = models.BooleanField(
        default=True,
        help_text=(
            "Controls whether wallet-funded tips are permitted."
        ),
    )

    allow_external_tips = models.BooleanField(
        default=True,
        help_text=(
            "Controls whether externally funded tips are permitted."
        ),
    )

    require_manual_review = models.BooleanField(
        default=False,
        help_text=(
            "When enabled, newly created tips may require manual "
            "review before settlement."
        ),
    )

    maximum_tip_frequency_per_day = models.PositiveIntegerField(
        default=25,
        validators=[
            MinValueValidator(1),
        ],
        help_text=(
            "Maximum number of tips a client may create within "
            "a rolling 24-hour window."
        ),
    )

    allow_other_reason_tips = models.BooleanField(
        default=True,
        help_text=(
            "Controls whether clients may create freeform "
            "'other' attribution tips."
        ),
    )

    is_active = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "Only one policy should be active at a time."
        ),
    )

    version = models.PositiveIntegerField(
        default=1,
        help_text=(
            "Monotonic version used for historical snapshots."
        ),
    )

    effective_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Optional activation timestamp for scheduled rollout."
        ),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tip_policies",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_tip_policies",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=[
                    "is_active",
                ],
                name="tip_policy_active_idx",
            ),
            models.Index(
                fields=[
                    "effective_from",
                ],
                name="tip_policy_effective_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(writer_percentage__gte=0)
                    & models.Q(platform_percentage__gte=0)
                ),
                name="tip_policy_percentages_positive",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.name} "
            f"(v{self.version})"
        )

    def clean(self) -> None:
        """
        Validate policy integrity.
        """
        super().clean()

        total_percentage = (
            self.writer_percentage
            + self.platform_percentage
        )

        if total_percentage != Decimal("100.00"):
            raise ValidationError(
                {
                    "writer_percentage": (
                        "Writer and platform percentages "
                        "must total 100%."
                    ),
                }
            )

        if (
            self.risk_review_threshold
            < self.minimum_tip_amount
        ):
            raise ValidationError(
                {
                    "risk_review_threshold": (
                        "Risk review threshold cannot be "
                        "lower than minimum tip amount."
                    ),
                }
            )

    def save(
        self,
        *args,
        **kwargs,
    ) -> None:
        """
        Persist policy safely.
        """
        self.full_clean()

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)