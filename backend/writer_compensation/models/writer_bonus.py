from decimal import Decimal
from django.db import models
from django.utils.timezone import now


class WriterBonus(models.Model):
    """
    Central ledger for all writer bonuses.

    This is the single source of truth for money earned via bonuses.
    Every bonus type is stored here for audit, reconciliation, and payout.
    """

    class BonusType(models.TextChoices):
        PERFORMANCE = "performance", "Performance Bonus"
        MILESTONE = "milestone", "Milestone Bonus"
        REFERRAL = "referral", "Referral Bonus"
        RETENTION = "retention", "Retention Bonus"
        MANUAL = "manual", "Manual Adjustment"

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="bonuses"
    )

    bonus_type = models.CharField(
        max_length=20,
        choices=BonusType.choices
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    currency = models.CharField(
        max_length=10,
        default="USD"
    )

    reason = models.TextField()

    compensation_event = models.ForeignKey(
        "writer_compensation.CompensationEvent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bonuses"
    )

    idempotency_key = models.CharField(
        max_length=255,
        unique=True
    )

    metadata = models.JSONField(
        default=dict,
        blank=True
    )
    notes = models.TextField(
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "writer_bonuses"
        indexes = [
            models.Index(fields=["writer", "bonus_type"]),
            models.Index(fields=["idempotency_key"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.writer.id} | {self.bonus_type} | {self.amount}"


class MilestoneBonus(models.Model):
    """
    Tracks milestone achievements so bonuses are never double-paid.
    """

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="milestone_bonus_records"
    )

    milestone = models.IntegerField() # e.g. 100 orders, 250 orders

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    compensation_event = models.ForeignKey(
        "writer_compensation.CompensationEvent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    awarded_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "writer_milestone_bonuses"
        unique_together = ("writer", "milestone")
        indexes = [
            models.Index(fields=["writer", "milestone"]),
        ]

    def __str__(self):
        return f"{self.writer.id} milestone {self.milestone}"


class ReferralBonus(models.Model):
    """
    Tracks referral-based earnings per order or period.
    Prevents duplicate payouts for the same referred activity.
    """

    referrer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="referral_bonus_records"
    )

    referred_writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="earned_referral_bonuses"
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    compensation_event = models.ForeignKey(
        "writer_compensation.CompensationEvent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    idempotency_key = models.CharField(
        max_length=255,
        unique=True
    )

    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "writer_referral_bonuses"
        indexes = [
            models.Index(fields=["referrer", "referred_writer"]),
            models.Index(fields=["order"]),
        ]

    def __str__(self):
        return f"{self.referrer.id} → {self.referred_writer.id} | {self.amount}"


class RetentionBonus(models.Model):
    """
    Monthly retention reward tracking.

    Ensures writers are rewarded for consistency, not just volume.
    """

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="retention_bonus_records"
    )

    month = models.DateField() # store first day of month

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    eligible = models.BooleanField(default=False)

    compensation_event = models.ForeignKey(
        "writer_compensation.CompensationEvent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    awarded_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "writer_retention_bonuses"
        unique_together = ("writer", "month")
        indexes = [
            models.Index(fields=["writer", "month"]),
        ]

    def __str__(self):
        return f"{self.writer.id} | {self.month} | {self.amount}"


class PerformanceBonusSnapshot(models.Model):
    """
    Snapshot of performance metrics at time of bonus calculation.

    Prevents disputes when performance changes after payout.
    """

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="performance_bonus_snapshots"
    )

    order_id = models.IntegerField()

    rating = models.DecimalField(max_digits=3, decimal_places=2)

    completion_rate = models.DecimalField(max_digits=5, decimal_places=2)

    base_amount = models.DecimalField(max_digits=12, decimal_places=2)

    bonus_rate = models.DecimalField(max_digits=5, decimal_places=2)

    bonus_amount = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "writer_performance_bonus_snapshots"
        indexes = [
            models.Index(fields=["writer", "order_id"]),
        ]

    def __str__(self):
        return f"{self.writer.id} order {self.order_id} bonus {self.bonus_amount}"