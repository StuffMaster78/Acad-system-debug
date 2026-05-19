from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from tips.constants import TIP_CURRENCY
from tips.enums.tip_source_type import TipSourceType
from tips.enums.tip_status import TipStatus


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from payments_processor.models.payment_intent import PaymentIntent


class Tip(models.Model):
    """
    Core financial tipping record.

    This model represents the canonical tipping transaction within the
    platform.

    Responsibilities:
    - stores gross financial truth
    - stores lifecycle state
    - stores sender/receiver relationships
    - links payment orchestration references
    - acts as the root aggregate for tip-related snapshots/traces

    This model intentionally avoids:
    - settlement calculations
    - orchestration logic
    - payment provider logic
    - wallet mutation logic
    """

    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_tips",
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="received_tips",
    )

    gross_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
        help_text=(
            "Total amount paid by the client in USD."
        ),
    )

    currency = models.CharField(
        max_length=3,
        default=TIP_CURRENCY,
        editable=False,
    )

    source_type = models.CharField(
        max_length=32,
        choices=TipSourceType.choices,
        db_index=True,
    )

    status = models.CharField(
        max_length=32,
        choices=TipStatus.choices,
        default=TipStatus.PENDING,
        db_index=True,
    )

    payment_intent = models.OneToOneField(
        "payments_processor.PaymentIntent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tip",
    )
    wallet_hold = models.ForeignKey(
        "wallets.WalletHold",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tips",
    )

    active_policy = models.ForeignKey(
        "tips.TipPolicy",
        on_delete=models.PROTECT,
        related_name="tips",
    )

    requires_manual_review = models.BooleanField(
        default=False,
        help_text=(
            "Whether this tip requires administrative review "
            "before settlement."
        ),
    )

    manually_reviewed = models.BooleanField(
        default=False,
    )

    manually_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_tips",
    )

    manually_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    settlement_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Internal settlement correlation reference."
        ),
    )

    client_note = models.TextField(
        blank=True,
        help_text=(
            "Optional message attached by the client."
        ),
    )

    is_settled = models.BooleanField(
        default=False,
        db_index=True,
    )
    settled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failure_reason = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    gross_amount_cents = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total tip amount in minor currency units.",
    )

    writer_share_cents = models.PositiveBigIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Writer payout portion in minor currency units.",
    )

    platform_fee_cents = models.PositiveBigIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Platform fee portion in minor currency units.",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=[
                    "sender",
                    "created_at",
                ],
                name="tip_sender_created_idx",
            ),
            models.Index(
                fields=[
                    "receiver",
                    "created_at",
                ],
                name="tip_receiver_created_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "created_at",
                ],
                name="tip_status_created_idx",
            ),
            models.Index(
                fields=[
                    "source_type",
                    "created_at",
                ],
                name="tip_source_created_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(gross_amount__gt=0),
                name="tip_gross_amount_positive",
            ),
            models.CheckConstraint(
                check=~models.Q(sender=models.F("receiver")),
                name="tip_sender_receiver_different",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Tip {self.public_id} "
            f"({self.gross_amount} {self.currency})"
        )

    # @property
    # def is_settled(self) -> bool:
    #     """
    #     Determine whether the tip completed successfully.
    #     """
    #     return self.status == TipStatus.SUCCEEDED

    @property
    def is_failed(self) -> bool:
        """
        Determine whether the tip failed.
        """
        return self.status == TipStatus.FAILED
