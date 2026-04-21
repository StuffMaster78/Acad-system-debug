from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError

from payments_processor.constants import DEFAULT_CURRENCY, ZERO_DECIMAL
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
    This is provider rail truth, not settlement truth.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.PROTECT,
        related_name="payment_intents"
    )
    reference = models.CharField(
        max_length=64,
        unique=True,
    )
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
            models.Index(fields=["website", "reference"]),
            models.Index(fields=["provider", "provider_intent_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["application_status"]),
            models.Index(fields=["purpose"]),
            models.Index(fields=["website", "client", "created_at"]),
        ]
        constraints = [
                models.CheckConstraint(
                    check=models.Q(amount__gt=ZERO_DECIMAL),
                    name="ppi_amount_gt_zero",
                ),
                models.CheckConstraint(
                    check=models.Q(amount_refunded__gte=ZERO_DECIMAL),
                    name="ppi_amount_refunded_gte_zero",
                ),
            ]
        
    def clean(self) -> None:
        super().clean()

        if self.amount_refunded > self.amount:
            raise ValidationError(
                {"amount_refunded": "Refunded amount cannot exceed payment amount."}
            )

        if bool(self.payable_content_type) != bool(self.payable_object_id):
            raise ValidationError(
                "Both payable_content_type and payable_object_id must be set together."
            )

    @property
    def refundable_amount(self) -> Decimal:
        return self.amount - self.amount_refunded

    def __str__(self) -> str:
        return f"{self.reference} [{self.status}]"