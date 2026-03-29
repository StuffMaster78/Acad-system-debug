import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from decimal import Decimal
from order_payments_management.models.payments import PaymentRecord
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
    ]

def generate_reference_id():
    return uuid.uuid4().hex


class ClassBundlePurchase(models.Model):
    """
    Represents a class bundle purchase made by a user.

    Attributes:
        user: The purchaser.
        bundle: The purchased bundle.
        payment: The payment record used.
        purchased_at: Timestamp of purchase.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    bundle = models.ForeignKey(
        "class_management.ClassBundle",
        on_delete=models.CASCADE,
        related_name="class_bundles_payments"
    )
    payment = models.OneToOneField(
        PaymentRecord, on_delete=models.CASCADE,
        related_name="bundle_purchase"
    )
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → {self.bundle}"
