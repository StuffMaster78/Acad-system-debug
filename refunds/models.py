from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
from orders.models import Order
from websites.models import Website
from order_payments_management.models import OrderPayment 
import uuid

def generate_reference_code():
    return uuid.uuid4().hex 
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
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='refunds_for_client'
    )
    order_payment = models.ForeignKey(
        OrderPayment,
        on_delete=models.CASCADE,
        related_name="refunds"
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
        related_name="processed_refunds"
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
    
class RefundRequest(models.Model):
    """
    Represents a refund request initiated by a client.

    Attributes:
        payment: Payment being refunded.
        requested_by: Who filed the refund request.
        reason: Stated reason for refund.
        status: Current lifecycle status of the request.
        decision_notes: Admin notes explaining the decision.
        reviewed_by: Admin who approved/rejected.
        created_at: When the request was filed.
        reviewed_at: When the request was resolved.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("refunded", "Refunded"),
        ("failed", "Failed"),
    ]

    payment = models.OneToOneField(
        "payments.PaymentRecord", on_delete=models.CASCADE,
        related_name="refund_request"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="refund_requests"
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    decision_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reviewed_refunds"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"RefundRequest for {self.payment.reference_id}"

class RefundTransaction(models.Model):
    """
    Represents the actual refund action performed on a payment.

    Attributes:
        request: The refund request this transaction fulfills.
        amount: Amount refunded.
        method: Refund method used (Stripe, Wallet, Manual).
        status: Status of the refund execution.
        reference_id: External refund ID (e.g. Stripe).
        metadata: Extra data like Stripe response or wallet log.
        created_at: When the refund was triggered.
        completed_at: When the refund was completed.
    """

    METHOD_CHOICES = [
        ("stripe", "Stripe"),
        ("wallet", "Wallet"),
        ("manual", "Manual"),
    ]

    STATUS_CHOICES = [
        ("initiated", "Initiated"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    request = models.ForeignKey(
        RefundRequest, on_delete=models.CASCADE,
        related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reference_id = models.CharField(
        max_length=100, blank=True, null=True
    )
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.method} refund of {self.amount}"

class RefundLog(models.Model):
    """
    Logs the details of a refund action. Used to track and audit refund activities.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='refund_logs'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="refund_logs",
        help_text="The order related to the refund"
    )
    refund = models.ForeignKey(
        Refund,
        on_delete=models.CASCADE,
        related_name="logs",
        help_text="The refund associated with this log"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="refund_logs",
        help_text="The client who initiated the refund"
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
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="refund_processed_logs",
        help_text="User who processed the refund"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processed', 'Processed'),
            ('rejected', 'Rejected')
        ],
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
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='refund_receipt'
    )
    refund = models.OneToOneField(
        Refund, on_delete=models.CASCADE,
        related_name="receipt"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Total amount refunded"
    )
    order_payment = models.ForeignKey(
        OrderPayment,
        on_delete=models.CASCADE,
        related_name="refund_receipt"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="refund_receipts"
    )

    reason = models.TextField(
        blank=True, null=True,
        help_text="Reason for the refund"
    )

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_receipts"
    )

    generated_at = models.DateTimeField(auto_now_add=True)

    reference_code = models.CharField(
        max_length=64, unique=True,
        default=generate_reference_code, blank=True
    )

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = uuid.uuid4().hex[:16]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receipt {self.reference_code} for Refund {self.refund.id}"