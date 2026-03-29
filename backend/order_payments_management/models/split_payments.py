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
from order_payments_management.models.logs import PaymentLog


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


class SplitPayment(models.Model):
    """
    Manages split payments where a client pays with multiple payment methods.
    Example: Half from wallet, half via card.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='split_order_payments'
    )
    payment = models.ForeignKey(
        "OrderPayment",
        on_delete=models.CASCADE,
        related_name="split_payments"
    )
    method = models.CharField(max_length=50)  # Card, Wallet, PayPal, etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def process_split_payment(cls, payment, split_data):
        """Processes split payments using bulk create."""
        total_paid = sum(data['amount'] for data in split_data)
        if total_paid != payment.discounted_amount:
            raise ValueError("Total split payments do not match order amount.")

        split_payments = [cls(payment=payment, website=payment.website, method=data['method'], amount=data['amount']) for data in split_data]
        cls.objects.bulk_create(split_payments)

        if total_paid == payment.discounted_amount:
            payment.mark_paid()