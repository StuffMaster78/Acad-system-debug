import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from decimal import Decimal
from wallet.models import Wallet
from django.core.exceptions import ValidationError
from discounts.models.discount import Discount 
from django.utils.timezone import now
from referrals.models import Referral, ReferralBonusConfig
from websites.models.websites import Website
from order_payments_management.models.payments import OrderPayment

STATUS_CHOICES = [
        ("pending", "Pending"),
        ("unpaid", "Unpaid"),
        ("succeeded", "Succeeded"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("partially_refunded", "Partially Refunded"),
        ("fully_refunded", "Fully Refunded"),
        ("refunded", "Refunded"),
        ("disputed", "Disputed"),
        ("under_review", "Under Review"),
    ]

PAYMENT_TYPE_CHOICES = [
        ("standard", "Standard Order"),
        ("predefined_special", "Predefined Special Order"),
        ("estimated_special", "Estimated Special Order"),
        ("special_installment", "Special Order Installment"),
        ("class_payment", "Class Payment"),
        ("wallet_loading", "Wallet Loading/Top-up"),
        ("tip", "Tip Payment"),
        ("invoice", "Standalone Invoice"),
    ]

def generate_reference_id():
    return uuid.uuid4().hex


class PaymentDispute(models.Model):
    """
    Manages disputes for failed or incorrect payments.
    Allows clients to raise disputes, which can be reviewed and resolved by admins.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("under_review", "Under Review"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_payment_dispute'
    )
    payment = models.ForeignKey(
        "OrderPayment",
        on_delete=models.CASCADE,
        related_name="disputes"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="disputes"
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not getattr(self, 'website_id', None):
            try:
                if getattr(self, 'payment', None) and getattr(self.payment, 'website_id', None):
                    self.website_id = self.payment.website_id
                elif getattr(self, 'client', None) and getattr(self.client, 'website_id', None):
                    self.website_id = self.client.website_id
            except Exception:
                pass
        super().save(*args, **kwargs)

    def mark_resolved(self):
        """
        Marks the dispute as resolved and updates the payment status to refunded.
        """
        self.status = "resolved"
        self.resolved_at = timezone.now()
        self.save()
        self.payment.status = "refunded"
        self.payment.save()