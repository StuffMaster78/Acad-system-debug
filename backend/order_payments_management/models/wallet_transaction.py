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
        ("other", "other"),
    ]

def generate_reference_id():
    return uuid.uuid4().hex


class WalletTransaction(models.Model):
    """
    Represents a wallet transaction for a user.

    Attributes:
        user: The user performing the transaction.
        amount: Amount credited or debited.
        direction: Transaction direction (credit or debit).
        purpose: Reason for the transaction.
        status: Status of the transaction.
        stripe_payment_intent_id: Stripe intent used (if any).
        reference_id: Unique internal reference.
        created_at: Creation timestamp.
    """

    DIRECTION_CHOICES = [
        ("credit", "Credit"),
        ("debit", "Debit"),
    ]

    PURPOSE_CHOICES = [
        ("funding", "Funding"),
        ("payment", "Payment"),
        ("adjustment", "Adjustment"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="wallet_transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    stripe_payment_intent_id = models.CharField(
        max_length=100, null=True, blank=True
    )
    reference_id = models.CharField(
        max_length=64, unique=True, default=generate_reference_id
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.direction} | {self.amount}"

