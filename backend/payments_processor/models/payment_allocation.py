from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from payments_processor.constants import DEFAULT_CURRENCY, ZERO_DECIMAL
from payments_processor.enums import (
    PaymentAllocationStatus,
    PaymentAllocationType,
)


class PaymentAllocation(models.Model):
    """
    Represents one funding portion for a payable.

    Wallet allocation should be backed by a WalletHold.
    External allocation should be backed by a PaymentIntent.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.PROTECT,
        related_name="payment_allocations",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payment_allocations",
    )

    reference = models.CharField(
        max_length=64,
        unique=True,
    )

    payable_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="payment_allocation_payables",
    )
    payable_object_id = models.PositiveBigIntegerField()
    payable = GenericForeignKey(
        "payable_content_type",
        "payable_object_id",
    )

    allocation_type = models.CharField(
        max_length=32,
        choices=PaymentAllocationType.choices,
    )
    status = models.CharField(
        max_length=32,
        choices=PaymentAllocationStatus.choices,
        default=PaymentAllocationStatus.PENDING,
    )

    currency = models.CharField(
        max_length=10,
        default=DEFAULT_CURRENCY,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    wallet_hold = models.OneToOneField(
        "wallets.WalletHold",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payment_allocation",
    )
    payment_intent = models.OneToOneField(
        "payments_processor.PaymentIntent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="allocation",
    )

    applied_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    released_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failure_reason = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["website", "customer", "created_at"]),
            models.Index(fields=["allocation_type", "status"]),
            models.Index(fields=["payable_content_type", "payable_object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.reference} [{self.allocation_type}:{self.status}]"