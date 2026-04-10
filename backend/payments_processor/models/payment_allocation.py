from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from payments_processor.constants import DEFAULT_CURRENCY
from payments_processor.enums import (
    PaymentAllocationStatus,
    PaymentAllocationType,
)


class PaymentAllocation(models.Model):
    """
    Represents one funding portion for a payable.
    Used for hybrid wallet plus gateway settlement.
    """

    reference = models.CharField(max_length=64, unique=True)

    customer = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="payment_allocations",
    )

    payable_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
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

    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payment_allocations",
    )

    payment_intent = models.OneToOneField(
        "payments.PaymentIntent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="allocation",
    )

    reserved_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    failure_reason = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["customer", "created_at"]),
            models.Index(fields=["allocation_type", "status"]),
            models.Index(fields=["payable_content_type", "payable_object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.reference} [{self.allocation_type}:{self.status}]"