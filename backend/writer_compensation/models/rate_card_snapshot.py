"""
writer_compensation/models/rate_card_snapshot.py

Immutable financial record of the pay rates that applied to a writer
at the moment they were assigned to a specific order.

WHY THIS EXISTS
---------------
WriterLevelSettings is mutable. Admins edit rates over time.
If a writer is promoted mid-month, their level settings change.
Without a snapshot, any earnings recalculation would use the NEW
rates, not the rates that applied when the order was assigned.

This model freezes the rates. Once created, it is never updated.
It is the source document for all earnings calculations on that order.

WHERE IT LIVES
--------------
writer_compensation — not writer_management, not orders.

orders        → what work was done (pages, deadline, status)
writer_management → what rates exist per level (WriterLevelSettings)
writer_compensation → what this writer was paid (this model + WriterPayment)

CREATION
--------
Created exactly once per order assignment by:
    writer_compensation.services.rate_card_snapshot_service
        .RateCardSnapshotService.capture(writer_profile, order)

Called from:
    order_actions.services.assignment_service
        .AssignmentService.assign(order, writer_profile)

READS
-----
    writer_compensation.services.earnings_calculator
        .EarningsCalculator.calculate(snapshot, order)

NEVER READS FROM WriterLevelSettings DIRECTLY AFTER CREATION.
"""

from decimal import Decimal

from django.db import models


class RateCardSnapshot(models.Model):
    """
    Immutable copy of WriterLevelSettings captured at order assignment.

    All fields are copied by value from WriterLevelSettings at the
    moment of assignment. No FKs to WriterLevel or WriterLevelSettings
    — those rows can be edited freely without affecting this record.

    This model has two FKs:
        writer  → writer_management.WriterProfile
        order   → orders.Order

    Neither writer_management nor orders imports from writer_compensation,
    so this placement introduces no circular dependency.
    """

    # ----------------------------------------------------------------
    # LINKS
    # ----------------------------------------------------------------

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="rate_card_snapshots",
    )

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="rate_card_snapshots",
        help_text="The writer this rate card applied to.",
    )

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="rate_card_snapshot",
        help_text=(
            "The order this snapshot was captured for. "
            "OneToOne — one snapshot per order, always."
        ),
    )

    # ----------------------------------------------------------------
    # LEVEL IDENTITY SNAPSHOT
    # Captures the level name and earning mode by value.
    # Not a FK — level names can be edited; the snapshot preserves
    # what the level was called when the order was assigned.
    # ----------------------------------------------------------------

    level_name = models.CharField(
        max_length=50,
        help_text="WriterLevel.name at time of assignment.",
    )

    earning_mode = models.CharField(
        max_length=30,
        help_text="WriterLevelSettings.EarningMode value at assignment.",
    )
    rate_card_version = models.PositiveIntegerField(
        default=1,
        help_text=(
            "Version of the compensation/rate-card structure "
            "used when this snapshot was captured."
        ),
    )

    # ----------------------------------------------------------------
    # EARNINGS CONFIGURATION SNAPSHOT
    # Copied from WriterLevelSettings by value.
    # ----------------------------------------------------------------

    base_pay_per_page = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    base_pay_per_slide = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    base_pay_per_chart = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    additional_page_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    additional_slide_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    additional_chart_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # ----------------------------------------------------------------
    # URGENCY SNAPSHOT
    # ----------------------------------------------------------------

    urgent_time_threshold_hours = models.PositiveSmallIntegerField(
        default=6,
        help_text=(
            "Orders due within this many hours are treated as urgent. "
            "Snapshot of WriterLevelSettings.urgent_time_threshold_hours."
        ),
    )

    urgent_order_surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Flat surcharge added per page for urgent orders.",
    )

    urgent_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
        help_text=(
            "Multiplier applied to base earnings for urgent orders. "
            "1.00 = no uplift."
        ),
    )

    # ----------------------------------------------------------------
    # TIP SPLIT SNAPSHOT
    # ----------------------------------------------------------------

    tip_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        help_text=(
            "Percentage of tips the writer retains. "
            "100.00 = full tip pass-through."
        ),
    )

    # ----------------------------------------------------------------
    # IMMUTABILITY METADATA
    # ----------------------------------------------------------------

    snapshotted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this snapshot was captured. Set once, never updated.",
    )

    currency = models.CharField(
        max_length=10,
        default="USD",
    )

    settings_updated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # ----------------------------------------------------------------
    # META
    # ----------------------------------------------------------------

    class Meta:
        verbose_name = "Rate Card Snapshot"
        verbose_name_plural = "Rate Card Snapshots"
        indexes = [
            models.Index(
                fields=["writer", "snapshotted_at"],
                name="rate_snapshot_writer_time_idx",
            ),
            models.Index(
                fields=["website", "snapshotted_at"],
                name="rate_snapshot_site_time_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base_pay_per_page__gte=Decimal("0.00")),
                name="rate_snapshot_base_page_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(urgent_multiplier__gte=Decimal("1.00")),
                name="rate_snapshot_urgency_multiplier_gte_1",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(tip_percentage__gte=Decimal("0.00")) &
                    models.Q(tip_percentage__lte=Decimal("100.00"))
                ),
                name="rate_snapshot_tip_pct_range",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"RateCardSnapshot order={self.order.pk} "
            f"writer={self.writer.pk} "
            f"level={self.level_name}"
        )