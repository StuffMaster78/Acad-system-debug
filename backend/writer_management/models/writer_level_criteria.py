"""
Promotion and demotion thresholds for a writer level.

WHY SEPARATE FROM WriterLevel AND WriterLevelSettings
------------------------------------------------------
WriterLevel       = what the level is called and its position in hierarchy
WriterLevelSettings = what we pay writers at this level (rate card)
WriterLevelCriteria = what a writer must achieve to reach / stay at this level

Three distinct concerns. Keeping them separate means:
    - Rate changes don't touch promotion rules
    - Promotion rules don't touch rate cards
    - Level identity doesn't change when either is updated

USAGE
-----
Read by:
    writer_management.services.level_progression_service
        .LevelProgressionService.evaluate(writer_profile)

Called weekly by Celery Beat task:
    writer_management.tasks.level_progression_tasks
        .evaluate_all_writer_levels

The service compares WriterPerformanceSnapshot fields against
these thresholds to decide promotion or demotion.

NULL FIELDS
-----------
max_* fields (max_revision_rate, max_lateness_rate, max_dispute_rate)
are nullable. Null means "no upper bound enforced for this level."
Useful for entry-level tiers where you want to promote freely
without penalising new writers for imperfect early performance.

min_* fields default to 0 meaning "no minimum required."
"""

from decimal import Decimal

from django.db import models


class WriterLevelCriteria(models.Model):
    """
    Promotion and demotion thresholds for a single writer level.

    One row per WriterLevel (OneToOne).
    Created by admin when configuring a level.

    All threshold comparisons are done by LevelProgressionService
    against WriterPerformanceSnapshot fields — never against live
    counters on WriterProfile or WriterPerformance.

    This ensures promotion decisions are always based on a consistent
    time-window snapshot, not a noisy real-time counter.
    """

    level = models.OneToOneField(
        "writer_management.WriterLevel",
        on_delete=models.CASCADE,
        related_name="criteria",
        help_text=(
            "The level these thresholds apply to. "
            "A writer must meet ALL promotion thresholds to be promoted "
            "TO this level, and must not breach any demotion threshold "
            "to remain AT the level below this one."
        ),
    )

    # ----------------------------------------------------------------
    # PROMOTION THRESHOLDS
    # Writer must meet ALL of these to be promoted to this level.
    # Evaluated against WriterPerformanceSnapshot for the review period.
    # ----------------------------------------------------------------

    min_composite_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Minimum composite performance score required. "
            "Computed by composite_score_service from weighted metrics."
        ),
    )

    min_orders_completed = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Minimum lifetime completed orders required. "
            "Compared against WriterPerformance.completed_orders."
        ),
    )

    min_avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Minimum average rating required (0.00–5.00). "
            "Compared against WriterPerformanceSnapshot.average_rating."
        ),
    )

    min_completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Minimum order completion rate as a percentage (0–100). "
            "Compared against WriterPerformanceSnapshot.completion_rate."
        ),
    )

    min_evaluation_periods = models.PositiveSmallIntegerField(
        default=1,
        help_text=(
            "Minimum number of consecutive evaluation periods a writer "
            "must meet the promotion thresholds before being promoted. "
            "Prevents one-off good weeks from triggering premature promotion."
        ),
    )

    # ----------------------------------------------------------------
    # DEMOTION THRESHOLDS
    # Breach of ANY of these triggers a demotion review.
    # Null means the threshold is not enforced for this level.
    # ----------------------------------------------------------------

    max_revision_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Maximum acceptable revision rate as a percentage. "
            "Null = not enforced. "
            "Compared against WriterPerformanceSnapshot.revision_rate."
        ),
    )

    max_lateness_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Maximum acceptable lateness rate as a percentage. "
            "Null = not enforced. "
            "Compared against WriterPerformanceSnapshot.lateness_rate."
        ),
    )

    max_dispute_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Maximum acceptable dispute rate as a percentage. "
            "Null = not enforced. "
            "Compared against WriterPerformanceSnapshot.dispute_rate."
        ),
    )

    max_cancellation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Maximum acceptable cancellation rate as a percentage. "
            "Null = not enforced."
        ),
    )

    # ----------------------------------------------------------------
    # CONFIGURATION
    # ----------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        help_text=(
            "When False, this level is excluded from automatic "
            "promotion/demotion evaluation. Useful while configuring "
            "a new level before publishing it."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Level Criteria"
        verbose_name_plural = "Writer Level Criteria"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    min_avg_rating__gte=Decimal("0.00"),
                    min_avg_rating__lte=Decimal("5.00"),
                ),
                name="level_criteria_rating_range",
            ),
            models.CheckConstraint(
                condition=models.Q(min_completion_rate__gte=Decimal("0.00")) &
                          models.Q(min_completion_rate__lte=Decimal("100.00")),
                name="level_criteria_completion_rate_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(max_revision_rate__isnull=True) |
                    (
                        models.Q(max_revision_rate__gte=Decimal("0.00")) &
                        models.Q(max_revision_rate__lte=Decimal("100.00"))
                    )
                ),
                name="level_criteria_revision_rate_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(max_lateness_rate__isnull=True) |
                    (
                        models.Q(max_lateness_rate__gte=Decimal("0.00")) &
                        models.Q(max_lateness_rate__lte=Decimal("100.00"))
                    )
                ),
                name="level_criteria_lateness_rate_range",
            ),
            models.CheckConstraint(
                condition=models.Q(min_evaluation_periods__gte=1),
                name="level_criteria_min_periods_gte_1",
            ),
        ]

    def __str__(self) -> str:
        return f"WriterLevelCriteria → {self.level}"

    # ----------------------------------------------------------------
    # EVALUATION HELPERS
    # Used by LevelProgressionService — no DB queries here.
    # ----------------------------------------------------------------

    def meets_promotion_thresholds(self, snapshot) -> tuple[bool, list[str]]:
        """
        Check whether a performance snapshot meets all promotion thresholds.

        Args:
            snapshot: WriterPerformanceSnapshot instance.

        Returns:
            (meets: bool, failures: list[str])
            failures is empty when meets is True.
        """
        failures = []

        if snapshot.composite_score is None or \
                snapshot.composite_score < self.min_composite_score:
            failures.append(
                f"composite_score {snapshot.composite_score} "
                f"< required {self.min_composite_score}"
            )

        if snapshot.average_rating is None or \
                snapshot.average_rating < self.min_avg_rating:
            failures.append(
                f"avg_rating {snapshot.average_rating} "
                f"< required {self.min_avg_rating}"
            )

        if snapshot.completion_rate < self.min_completion_rate:
            failures.append(
                f"completion_rate {snapshot.completion_rate}% "
                f"< required {self.min_completion_rate}%"
            )

        return len(failures) == 0, failures

    def breaches_demotion_thresholds(self, snapshot) -> tuple[bool, list[str]]:
        """
        Check whether a performance snapshot breaches any demotion threshold.

        Args:
            snapshot: WriterPerformanceSnapshot instance.

        Returns:
            (breached: bool, breaches: list[str])
            breaches is empty when breached is False.
        """
        breaches = []

        if self.max_revision_rate is not None and \
                snapshot.revision_rate > self.max_revision_rate:
            breaches.append(
                f"revision_rate {snapshot.revision_rate}% "
                f"> max {self.max_revision_rate}%"
            )

        if self.max_lateness_rate is not None and \
                snapshot.lateness_rate > self.max_lateness_rate:
            breaches.append(
                f"lateness_rate {snapshot.lateness_rate}% "
                f"> max {self.max_lateness_rate}%"
            )

        if self.max_dispute_rate is not None and \
                snapshot.dispute_rate > self.max_dispute_rate:
            breaches.append(
                f"dispute_rate {snapshot.dispute_rate}% "
                f"> max {self.max_dispute_rate}%"
            )

        if self.max_cancellation_rate is not None and \
                snapshot.cancellation_rate > self.max_cancellation_rate:
            breaches.append(
                f"cancellation_rate {snapshot.cancellation_rate}% "
                f"> max {self.max_cancellation_rate}%"
            )

        return len(breaches) > 0, breaches