from __future__ import annotations

from decimal import Decimal
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def generate_reference_code() -> str:
    """Return a unique receipt reference code."""
    return uuid.uuid4().hex


class Refund(models.Model):
    """
    Business workflow record for client refunds.

    Refund execution is delegated to wallets for wallet credits and to
    payments_processor.PaymentRefund for original payment method refunds.
    """

    MANUAL = "manual"
    AUTOMATED = "automated"

    TYPE_CHOICES = [
        (MANUAL, "Manual"),
        (AUTOMATED, "Automated"),
    ]

    METHOD_WALLET = "wallet"
    METHOD_EXTERNAL = "external"
    METHOD_SPLIT = "split"

    METHOD_CHOICES = [
        (METHOD_WALLET, "Wallet"),
        (METHOD_EXTERNAL, "Original Payment Method"),
        (METHOD_SPLIT, "Wallet and Original Payment Method"),
    ]

    PENDING = "pending"
    PROCESSED = "processed"
    REJECTED = "rejected"
    CANCELED = "canceled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PROCESSED, "Processed"),
        (REJECTED, "Rejected"),
        (CANCELED, "Canceled"),
    ]

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="refunds",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds",
    )
    order_payment = models.ForeignKey(
        "payments_processor.PaymentIntent",
        on_delete=models.PROTECT,
        related_name="refund_app_refunds",
    )
    payment_refund = models.ForeignKey(
        "payments_processor.PaymentRefund",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refund_workflows",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_refunds",
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=MANUAL,
    )
    wallet_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    external_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    refund_method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default=METHOD_WALLET,
    )
    reason = models.TextField(blank=True, default="")
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_refund_app_refunds",
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["website", "client", "created_at"]),
            models.Index(fields=["order_payment", "status"]),
            models.Index(fields=["status"]),
            models.Index(fields=["refund_method"]),
        ]

    def __str__(self) -> str:
        return (
            f"Refund {self.pk or 'new'} of {self.total_amount()} "
            f"for payment {self.order_payment.pk}"
        )

    def clean(self) -> None:
        """Validate refund amounts and destination consistency."""
        super().clean()

        if self.wallet_amount < Decimal("0.00"):
            raise ValidationError(
                {"wallet_amount": "Wallet refund cannot be negative."}
            )

        if self.external_amount < Decimal("0.00"):
            raise ValidationError(
                {"external_amount": "External refund cannot be negative."}
            )

        if self.total_amount() <= Decimal("0.00"):
            raise ValidationError("Refund amount must be greater than zero.")

        if (
            self.refund_method == self.METHOD_WALLET
            and self.external_amount > Decimal("0.00")
        ):
            raise ValidationError(
                {
                    "refund_method": (
                        "Wallet refunds cannot include external amount."
                    ),
                }
            )

        if (
            self.refund_method == self.METHOD_EXTERNAL
            and self.wallet_amount > Decimal("0.00")
        ):
            raise ValidationError(
                {
                    "refund_method": (
                        "External refunds cannot include wallet amount."
                    ),
                }
            )

    def save(self, *args, **kwargs) -> None:
        """Infer tenant, client, order, and destination before saving."""
        self._infer_related_fields()
        self._infer_refund_method()
        super().save(*args, **kwargs)

    def total_amount(self) -> Decimal:
        """Return the combined wallet and external refund amount."""
        return self.wallet_amount + self.external_amount

    @property
    def is_full_refund(self) -> bool:
        """Return whether this refund covers the whole payment amount."""
        payment_amount = getattr(
            self.order_payment,
            "amount",
            Decimal("0.00"),
        )
        return self.total_amount() >= payment_amount

    def _infer_related_fields(self) -> None:
        payment = getattr(self, "order_payment", None)
        if payment is None:
            return

        if not self.website_id and getattr(payment, "website_id", None):
            self.website_id = payment.website_id

        if not self.client_id and getattr(payment, "client_id", None):
            self.client_id = payment.client_id

        payable = getattr(payment, "payable", None)
        if not self.order and payable is not None:
            if payable.__class__._meta.label_lower == "orders.order":
                self.order = payable

    def _infer_refund_method(self) -> None:
        has_wallet = self.wallet_amount > Decimal("0.00")
        has_external = self.external_amount > Decimal("0.00")

        if has_wallet and has_external:
            self.refund_method = self.METHOD_SPLIT
        elif has_external:
            self.refund_method = self.METHOD_EXTERNAL
        else:
            self.refund_method = self.METHOD_WALLET


class RefundLog(models.Model):
    """Immutable audit log for refund workflow actions."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="refund_logs",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refund_logs",
    )
    refund = models.ForeignKey(
        Refund,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="refund_logs",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    action = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="refund_processed_logs",
    )
    status = models.CharField(max_length=20)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["website", "client", "created_at"]),
            models.Index(fields=["refund", "status"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.action} for refund {self.refund.pk} "
            f"amount={self.amount} status={self.status}"
        )


class RefundReceipt(models.Model):
    """Client-facing receipt for a processed refund."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="refund_receipts",
    )
    refund = models.OneToOneField(
        Refund,
        on_delete=models.CASCADE,
        related_name="receipt",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_payment = models.ForeignKey(
        "payments_processor.PaymentIntent",
        on_delete=models.PROTECT,
        related_name="refund_receipts",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="refund_receipts",
    )
    reason = models.TextField(blank=True, default="")
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_receipts",
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    reference_code = models.CharField(
        max_length=64,
        unique=True,
        default=generate_reference_code,
        blank=True,
    )

    class Meta:
        ordering = ["-generated_at", "-id"]

    def __str__(self) -> str:
        return f"Receipt {self.reference_code} for refund {self.refund.pk}"
