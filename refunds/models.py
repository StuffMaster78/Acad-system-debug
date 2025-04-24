from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
from orders.models import Order
from order_payments_management.models import OrderPayment 

class Refund(models.Model):
    """
    Represents a refund record. Supports wallet and external refunds.
    Allows both manual and automated refunds.
    """
    MANUAL = 'manual'
    AUTOMATED = 'automated'

    REFUND_TYPE_CHOICES = [
        (MANUAL, 'Manual'),
        (AUTOMATED, 'Automated'),
    ]

    METHOD_CHOICES = [
        ("wallet", "Wallet"),
        ("external", "External"),
    ]

    PENDING = 'pending'
    PROCESSED = 'processed'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSED, 'Processed'),
        (REJECTED, 'rejected'),
    ]

    order_payment = models.ForeignKey(
        OrderPayment, on_delete=models.CASCADE, related_name="refunds"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_refunds",
    )
    type = models.CharField(
        max_length=10,
        choices=REFUND_TYPE_CHOICES,
        default=MANUAL
    )
    wallet_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0
    )
    external_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0
    )
    refund_method = models.CharField(
        max_length=10, choices=METHOD_CHOICES, default="wallet"
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_refunds",
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return (
            f"Refund of ${self.total_amount()} for OrderPayment {self.payment.id}"
        )

    def total_amount(self):
        """
        Returns the total refunded amount (wallet + external).
        """
        return self.wallet_amount + self.external_amount
    

class RefundLog(models.Model):
    """
    Logs the details of a refund action. Used to track and audit refund activities.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="refund_logs",
        help_text="The order related to the refund"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount refunded"
    )
    source = models.CharField(
        max_length=100,
        help_text="Origin of the refund (manual, stripe-webhook, etc.)"
    )
    status = models.CharField(
        max_length=20,
        choices=[('success', 'Success'), ('failed', 'Failed')],
        help_text="Refund status"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Any additional metadata associated with the refund"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of the refund action"
    )

    def __str__(self):
        return (
            f"Refund of {self.amount} for Order {self.order.id} "
            f"from {self.source} - {self.status}"
        )


class RefundReceipt(models.Model):
    """
    Receipt for the refunded amount.
    """

    refund = models.OneToOneField(
        Refund, on_delete=models.CASCADE,
        related_name="receipt"
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    reference_code = models.CharField(
        max_length=64, unique=True,
        default="", blank=True
    )

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = uuid.uuid4().hex[:16]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receipt {self.reference_code} for Refund {self.refund.id}"