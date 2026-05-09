from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website
from writer_management.models.profile import WriterProfile

from writer_payments_management.enums.financial_event_enums import (
    FinancialEventSource,
)
from writer_payments_management.enums.financial_event_enums import (
    FinancialEventStatus,
)
from writer_payments_management.enums.financial_event_enums import (
    FinancialEventType,
)

User = settings.AUTH_USER_MODEL


class FinancialEvent(models.Model):
    """
    Immutable financial truth record.

    This represents all writer earnings and deductions
    before settlement or payout processing.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="financial_events",
    )

    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="financial_events",
    )

    event_type = models.CharField(
        max_length=64,
        choices=FinancialEventType.choices,
    )

    source = models.CharField(
        max_length=64,
        choices=FinancialEventSource.choices,
    )

    status = models.CharField(
        max_length=64,
        choices=FinancialEventStatus.choices,
        default=FinancialEventStatus.PENDING_CONFIRMATION,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=10,
        default="USD",
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    reference = models.CharField(
        max_length=255,
        blank=True,
    )

    external_reference = models.CharField(
        max_length=255,
        blank=True,
    )

    source_type = models.CharField(
        max_length=64,
        blank=True,
        help_text="order, special_order, class_session, tip, bonus",
    )

    source_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    related_event = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derivatives",
        help_text="Reversal or adjustment link",
    )

    settlement_period = models.ForeignKey(
        "writer_payments_management.SettlementPeriod",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="financial_events",
    )

    is_visible_to_writer = models.BooleanField(
        default=True,
    )

    is_risky = models.BooleanField(
        default=False,
    )

    is_locked = models.BooleanField(
        default=False,
    )

    matured_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    disputed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reversed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_financial_events",
    )
    idempotency_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
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
            models.Index(fields=["website", "writer"]),
            models.Index(fields=["event_type", "status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["source_type", "source_id"]),
            models.Index(
                fields=[
                    "website",
                    "writer",
                    "status",
                    "settlement_period",
                ],
                name="financial_event_settlement_idx",
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["website", "writer", "idempotency_key"],
                condition=models.Q(idempotency_key__isnull=False),
                name="unique_financial_event_idempotency",
            ),

            models.CheckConstraint(
                condition=~models.Q(amount=Decimal("0.00")),
                name="financial_event_amount_non_zero",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.writer.user.email} | "
            f"{self.event_type} | "
            f"{self.amount}"
        )

    @property
    def is_positive_event(self) -> bool:
        return self.amount >= Decimal("0.00")

    @property
    def is_negative_event(self) -> bool:
        return self.amount < Decimal("0.00")

    @property
    def can_be_settled(self) -> bool:
        return (
            self.status == FinancialEventStatus.MATURED
            and not self.is_locked
        )

    @property
    def affects_writer_balance(self) -> bool:
        return self.status in {
            FinancialEventStatus.MATURED,
            FinancialEventStatus.INCLUDED_IN_SETTLEMENT,
            FinancialEventStatus.PAID,
        }