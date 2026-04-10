from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from decimal import Decimal

from payments_processor.constants import DEFAULT_CURRENCY
from payments_processor.enums import (
    PaymentApplicationStatus,
    PaymentIntentPurpose,
    PaymentIntentStatus,
    PaymentProvider,
)


class PaymentIntent(models.Model):
    """
    Represents an external payment collection attempt.
    """

    reference = models.CharField(max_length=64, unique=True)

    client = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="payment_intents",
    )

    purpose = models.CharField(
        max_length=32,
        choices=PaymentIntentPurpose.choices,
    )

    provider = models.CharField(
        max_length=32,
        choices=PaymentProvider.choices,
    )

    status = models.CharField(
        max_length=32,
        choices=PaymentIntentStatus.choices,
        default=PaymentIntentStatus.CREATED,
    )

    application_status = models.CharField(
        max_length=32,
        choices=PaymentApplicationStatus.choices,
        default=PaymentApplicationStatus.NOT_APPLIED,
    )

    currency = models.CharField(
        max_length=10,
        default=DEFAULT_CURRENCY,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    amount_refunded = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    payable_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    payable_object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )
    payable = GenericForeignKey(
        "payable_content_type",
        "payable_object_id",
    )

    provider_intent_id = models.CharField(
        max_length=128,
        blank=True,
        default="",
    )

    provider_customer_id = models.CharField(
        max_length=128,
        blank=True,
        default="",
    )

    last_verified_at = models.DateTimeField(null=True, blank=True)
    verification_attempts = models.PositiveIntegerField(default=0)
    application_attempts = models.PositiveIntegerField(default=0)
    application_error = models.TextField(blank=True, default="")

    metadata = models.JSONField(default=dict, blank=True)

    expires_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["provider", "provider_intent_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["application_status"]),
            models.Index(fields=["purpose"]),
            models.Index(fields=["customer", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.reference} [{self.status}]"