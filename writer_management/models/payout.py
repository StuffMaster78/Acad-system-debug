from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import PermissionDenied
from websites.models import Website 
from writer_management.models.profile import WriterProfile
from orders.models import Order



class WriterPayoutPreference(models.Model):
    """
    Stores writer payout preferences.
    """
    PAYMENT_METHOD_CHOICES = [
        ("Bank Transfer", "Bank Transfer"),
        ("PayPal", "PayPal"),
        ("Crypto", "Crypto"),
        ("Mpesa", "Mpesa"),
        ("Other", "Other"),
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_payout_preference"
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="payout_preferences"
    )
    preferred_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, 
        default="Mpesa"
    )
    payout_threshold = models.DecimalField(
        max_digits=12, decimal_places=2, default=50.00,
        help_text="Minimum payout threshold."
    )
    account_details = models.JSONField(
        default=dict, blank=True,
        help_text="Payment account details (e.g., PayPal email, bank details)."
    )
    verified = models.BooleanField(
        default=False,
        help_text="Has the payout method been verified by an admin?"
    )
    allowed_currencies = models.JSONField(
        default=list, blank=True,
        help_text="Currencies allowed for this payout method."
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.writer.user.username} - {self.preferred_method}"

    def needs_verification(self):
        """Check if payout details require admin verification."""
        return not self.verified


class WriterPayment(models.Model):
    """
    Tracks payment history for writers.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_compensation"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Total payment amount."
    )
    bonuses = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0.00, help_text="Bonuses received."
    )
    fines = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0.00, help_text="Fines deducted."
    )
    tips = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0.00,
        help_text="Tips received."
    )
    converted_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text="Amount paid in the writer's local currency (e.g., KSH)."
    )
    conversion_rate = models.DecimalField(
        max_digits=10, decimal_places=4,
        null=True, blank=True,
        help_text="USD to KSH rate used at time of payment."
    )

    currency = models.CharField(
        max_length=5,
        default="USD",
        help_text="Currency in which the writer was paid (e.g., USD, KSH)."
    )
    payment_date = models.DateTimeField(
        auto_now_add=True, help_text="Date of payment."
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Payment description."
    )

    def __str__(self):
        return (
            f"Payment of ${self.amount} to {self.writer.user.username}"
             f"on {self.payment_date}"
        )
    
    def save(self, *args, **kwargs):
        if not self.writer.user.is_staff and self.conversion_rate is not None:
            raise PermissionDenied("Only admins can set conversion rates.")
        # Ensure website inferred
        if not getattr(self, 'website_id', None):
            try:
                self.website_id = self.writer.website_id
            except Exception:
                pass
        super().save(*args, **kwargs)


class WriterEarningsHistory(models.Model):
    """
    Tracks the writer's total earnings over different time periods.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_earning_history"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="earnings_history"
    )
    period_start = models.DateTimeField(
        help_text="Start date of the earnings period."
    )
    period_end = models.DateTimeField(
        help_text="End date of the earnings period."
    )
    total_earnings = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        help_text="Total earnings for the period."
    )
    orders_completed = models.PositiveIntegerField(
        default=0, 
        help_text="Number of completed orders during this period."
    )

    def __str__(self):
        return (
            f"Earnings for {self.writer.user.username}: "
            f"{self.period_start} - {self.period_end}"
        )

class CurrencyConversionRate(models.Model):
    """
    Stores conversion rates from USD to other currencies.
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        related_name="conversion_rates"
    )
    target_currency = models.CharField(
        max_length=10,
        default="KSH",
        help_text="The currency to convert to (e.g., KSH)."
    )
    rate = models.DecimalField(
        max_digits=10, decimal_places=4,
        help_text="Conversion rate from 1 USD to target currency."
    )
    effective_date = models.DateField(
        help_text="The date this rate became effective."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Currency Conversion Rate"
        verbose_name_plural = "Currency Conversion Rates"
        unique_together = ("website", "target_currency", "effective_date")

    def __str__(self):
        return (
            f"{self.target_currency} @ {self.rate} "
            f"(as of {self.effective_date})"
        )