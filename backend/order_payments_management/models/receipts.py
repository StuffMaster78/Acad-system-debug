import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from decimal import Decimal
from order_payments_management.models.invoice import generate_reference_id
from wallet.models import Wallet
from django.core.exceptions import ValidationError
from discounts.models.discount import Discount 
from django.utils.timezone import now
from referrals.models import Referral, ReferralBonusConfig
from websites.models.websites import Website


def generate_receipt_number():
    return f"RCT-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"

class PaymentReceipt(models.Model):
    """
    Represents a formal receipt issued for a completed payment.

    Attributes:
        payment: The related payment record.
        invoice: Optional linked invoice.
        issued_to: The user who made the payment.
        issued_by: The system or admin who issued the receipt.
        receipt_number: Unique receipt identifier.
        notes: Optional internal notes or remarks.
        metadata: Custom JSON info (tax, location, etc.).
        created_at: When the receipt was generated.
    """

    payment = models.OneToOneField(
        "PaymentRecord", on_delete=models.CASCADE,
        related_name="receipt"
    )
    invoice = models.ForeignKey(
        "Invoice", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="receipts"
    )
    issued_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="payment_receipts"
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="issued_receipts"
    )
    receipt_number = models.CharField(
        max_length=64, unique=True, default=generate_reference_id
    )
    notes = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt #{self.receipt_number} for {self.payment.reference_id}"


class ReceiptDeliveryLog(models.Model):
    """
    Tracks when a receipt was sent via email/SMS for audit purposes.
    """

    receipt = models.ForeignKey(
        "PaymentReceipt", on_delete=models.CASCADE,
        related_name="delivery_logs"
    )
    method = models.CharField(
        max_length=20, choices=[("email", "Email"), ("sms", "SMS")]
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    response = models.TextField(blank=True)

    def __str__(self):
        return f"{self.method} sent at {self.sent_at}"