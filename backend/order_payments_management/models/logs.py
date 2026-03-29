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
    ]

def generate_reference_id():
    return uuid.uuid4().hex

class PaymentLog(models.Model):
    """
    Stores logs for all payment-related actions.
    Useful for tracking and auditing payment transactions.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_payment_log'
    )
    payment = models.ForeignKey(
        "OrderPayment",
        on_delete=models.CASCADE,
        related_name="logs"
    )
    event = models.CharField(
        max_length=255,
        help_text="Example: 'Payment Completed', 'Refund Issued'"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    @classmethod
    def log_event(cls, payment, event, details=""):
        """
        Creates a log entry for a payment event.
        Example: "Refund Issued - Client refunded $20."
        """
        website = getattr(payment, 'website', None)
        if website is None:
            try:
                website = payment.order.website
            except Exception:
                from websites.models.websites import Website
                website = Website.objects.filter(is_active=True).first()
                if website is None:
                    website = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
        return cls.objects.create(payment=payment, event=event, details=details, website=website)


class AdminLog(models.Model):
    """
    Logs admin actions related to payments, disputes, and refunds.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='admin_log_payments'
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="logs"
    )
    action = models.CharField(max_length=255)  # Example: "Refund Processed"
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    @classmethod
    def log_action(cls, admin, action, details=""):
        """
        Creates a log entry for an admin action.
        """
        website_id = None
        try:
            website_id = getattr(admin, 'website_id', None)
        except Exception:
            website_id = None
        if website_id is None:
            try:
                from websites.models.websites import Website
                site = Website.objects.filter(is_active=True).first()
                if site is None:
                    site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                website_id = site.pk
            except Exception:
                pass
        return cls.objects.create(admin=admin, action=action, details=details, website_id=website_id)
    
